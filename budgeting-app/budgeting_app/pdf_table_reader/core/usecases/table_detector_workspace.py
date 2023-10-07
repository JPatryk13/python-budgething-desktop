from dataclasses import asdict, dataclass
import enum
import io
import logging
from typing import Any, Literal
from uuid import uuid4
from budgeting_app.utils.logging import CustomLoggerAdapter
from budgeting_app.utils.types import TypedObservableDict

from pdfplumber import table, page, _typing, display

from budgeting_app.pdf_table_reader.core.entities.models import ExplicitLineData, PDFFileWrapper, PDFPageWrapper, ImageWrapper, BASE_IMAGE_RESOLUTION


DEFAULT_TABLE_SETTINGS = {
    "vertical_strategy": "lines", 
    "horizontal_strategy": "lines",
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    "snap_tolerance": 3,
    "snap_x_tolerance": 3,
    "snap_y_tolerance": 3,
    "join_tolerance": 3,
    "join_x_tolerance": 3,
    "join_y_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3,
}

class TableDetectorWorkspace:
    """
    Detect tabular data based on given settings (or/and elements such as lines/squares
    - they are being appended to settings therefore I might ommit to mention them) and
    allow to retrieve that data along with updated image.
    """
    class AddPageMode(enum.Enum):
        AT_BEGGINING = 0
        AT_END = 1
        INSERT_AFTER = 2
        REPLACE = 3
        
    pdf_file: PDFFileWrapper
    logger: logging.LoggerAdapter
    
    def __init__(self, pdf_file: PDFFileWrapper, default_table_settings: table.T_table_settings = DEFAULT_TABLE_SETTINGS) -> None:
        
        self.logger = CustomLoggerAdapter.getLogger('pdf_table_reader', className='TableDetectorWorkspace')
        self.logger.debug('Inititalising TableDetectorWorkspace.')
        
        self.pdf_file = pdf_file
        
        for p in self.pdf_file.pages:
            p.table_settings = TypedObservableDict(default_table_settings)

    ###########################
    #        ADD PAGES        #
    ###########################
    
    def _is_replace_page_numbers_valid(self, replace_page_numbers: list[int], pages: list) -> tuple[bool, str | None]:
        """Validate if `replace_page_numbers` is correct given list of `pages`.

        Returns:
            tuple[bool, str | None]: flag whether the value `replace_page_numbers` is correct or
            not and if it isn't then an error msg is returned as well
        """
        if replace_page_numbers == []:
            # empty
            return False, 'Given replace_page_numbers list must not be ' \
                'empty when add_page_mode = self.AddPageMode.REPLACE'
        
        if min(replace_page_numbers) < 0 or max(replace_page_numbers) >= len(self.pdf_file.pages):
            # out of range
            return False, f'Each value from the replace_page_numbers must represent ' \
                f'a valid index of the pages list. Either {min(replace_page_numbers)} ' \
                f'>= 0 or {max(replace_page_numbers)} <  {len(self.pdf_file.pages)} are incorrect'
        
        if len(replace_page_numbers) > 1 and len(replace_page_numbers) != len(pages):
            # no suitable mapping canbe set up
            nums = list(set(replace_page_numbers))
            if nums[len(nums) - 1] - nums[0] != len(nums) - 1:
                return False, f'Given list replace_page_numbers when having more than one ' \
                    f'value must represent consecutive indices. Got {replace_page_numbers} instead.'
            
        return True, None
    
    def add_page(
        self, 
        page: PDFPageWrapper,
        *,
        add_page_mode: AddPageMode = AddPageMode.AT_END,
        insert_after_page_number: int = -1,
        replace_page_numbers: list[int] = []
    ) -> 'TableDetectorWorkspace':
        """Add page to the `pdf_file.pages` list. Allows to configure where the page is to be added.

        Args:
            - page (PDFPageWrapper): The page to add
            - add_page_mode (AddPageMode, optional): Configure where the page is to be added. Defaults
            to `AddPageMode.AT_END`.
            - insert_after_page_number (int, optional): Required when `add_page_mode` is set to
            AddPageMode.INSERT_AFTER. Index of the page after which the given one is to be inserted.
            Defaults to -1.
            - replace_page_numbers (list[int], optional): Required when `add_page_mode` is set to
            AddPageMode.REPLACE. List of page indices that need to be replaced with the given one.
            Must represent a list of consecutive indices. Defaults to [].

        Returns:
            TableDetectorWorkspace: Instance of self
        """
        
        if add_page_mode == self.AddPageMode.AT_BEGGINING:
            # add at the beggining
            self.pdf_file.pages = [page, *self.pdf_file.pages]
            
        elif add_page_mode == self.AddPageMode.AT_END:
            # add at the end
            self.pdf_file.pages.append(page)
            
        elif add_page_mode == self.AddPageMode.INSERT_AFTER:
            
            if 0 <= insert_after_page_number < len(self.pdf_file.pages):
                # insert after the item with given index
                self.pdf_file.pages = [
                    *self.pdf_file.pages[:insert_after_page_number + 1],
                    page,
                    *self.pdf_file.pages[insert_after_page_number + 1:]
                ]
                
            else:
                raise ValueError(f'Required: 0 <= insert_after_page_number < {len(self.pdf_file.pages)}, got insert_after_page_number={insert_after_page_number}')
            
        elif add_page_mode == self.AddPageMode.REPLACE:
            
            # validate replace_page_numbers
            replace_page_numbers_is_valid, error_msg = self._is_replace_page_numbers_valid(replace_page_numbers, [page])
            if not replace_page_numbers_is_valid:
                raise ValueError(error_msg)
            
            # remove duplicates
            nums = list(set(replace_page_numbers))
            
            self.pdf_file.pages = [
                *self.pdf_file.pages[:min(nums)],
                page,
                *self.pdf_file.pages[max(nums) + 1:]
            ]
        
        else:
            raise ValueError(f'Got incorrect value of add_page_mode: {add_page_mode}.')
        
        return self
    
    def add_pages(
        self,
        pages: list[PDFPageWrapper],
        *,
        add_page_mode: AddPageMode = AddPageMode.AT_END,
        insert_after_page_number: int = -1,
        replace_page_numbers: list[int] = []
    ) -> 'TableDetectorWorkspace':
        """Add pages to the `pdf_file.pages` list. Allows to configure where they are to be added.

        Args:
            - pages (PDFPageWrapper): Pages to add
            - add_page_mode (AddPageMode, optional): Configure where pages are to be added. Defaults
            to `AddPageMode.AT_END`.
            - insert_after_page_number (int, optional): Required when `add_page_mode` is set to
            `AddPageMode.INSERT_AFTER`. Index of the page after which the given ones are to be inserted.
            Defaults to -1.
            - replace_page_numbers (list[int], optional): Required when `add_page_mode` is set to
            `AddPageMode.REPLACE`. List of page indices that need to be replaced with the given ones.
            Must represent a list of consecutive indices. Defaults to [].

        Returns:
            TableDetectorWorkspace: Instance of self
        """
        
        if add_page_mode == self.AddPageMode.AT_END:
            self.pdf_file.pages = [*self.pdf_file.pages, *pages]
            
        elif add_page_mode == self.AddPageMode.AT_BEGGINING:
            self.pdf_file.pages = [*pages, *self.pdf_file.pages]
            
        elif add_page_mode == self.AddPageMode.INSERT_AFTER:
            if 0 <= insert_after_page_number < len(self.pdf_file.pages):
                # insert after the item with given index
                self.pdf_file.pages = [
                    *self.pdf_file.pages[:insert_after_page_number + 1],
                    *pages,
                    *self.pdf_file.pages[insert_after_page_number + 1:]
                ]
            else:
                raise ValueError(f'Required: 0 <= insert_after_page_number < {len(self.pdf_file.pages)}, got insert_after_page_number={insert_after_page_number}')
            
        elif add_page_mode == self.AddPageMode.REPLACE:
            
            # validate replace_page_numbers
            replace_page_numbers_is_valid, err_msg = self._is_replace_page_numbers_valid(replace_page_numbers, pages)
            if not replace_page_numbers_is_valid:
                raise ValueError(err_msg)
            
            # remove duplicates
            replace_ind = list(set(replace_page_numbers))
            if len(replace_ind) == 1 and replace_ind[0] == 0:
                self.pdf_file.pages = [*pages, *self.pdf_file.pages[1:]]
            elif replace_ind[len(replace_ind) - 1] - replace_ind[0] == len(replace_ind) - 1:
                # lists cosists of consecutive indices or it's just a signle number
                # the above condition works in both cases
                self.pdf_file.pages = [
                    *self.pdf_file.pages[:min(replace_ind)],
                    *pages,
                    *self.pdf_file.pages[max(replace_ind) + 1:]
                ]
            else:
                for i, page in enumerate(pages):
                    # 1:1 replace mapping - handle one by one
                    self.add_page(
                        page,
                        add_page_mode=add_page_mode,
                        replace_page_numbers=replace_page_numbers[i]
                    )
                
        return self
           
    def add_pages_from_file(
        self,
        pdf_file: PDFFileWrapper,
        *,
        add_pages_numbers: list[int] | Literal['all'] = 'all',
        add_page_mode: AddPageMode = AddPageMode.AT_END,
        insert_after_page_number: int = -1,
        replace_page_numbers: list[int] = []
    ) -> 'TableDetectorWorkspace':
        """Allows to add all or selected pages from PDFFileWrapper object.

        Args:
            - pdf_file (PDFFileWrapper): to pull the pages from
            - add_pages_numbers (list[int] | Literal[&#39;all&#39;], optional): Which pages to add.
            Defaults to 'all'.
            - add_page_mode (AddPageMode, optional): Configure where pages are to be added. Defaults
            to `AddPageMode.AT_END`.
            - insert_after_page_number (int, optional): Required when `add_page_mode` is set to
            `AddPageMode.INSERT_AFTER`. Index of the page after which the given ones are to be inserted.
            Defaults to -1.
            - replace_page_numbers (list[int], optional): Required when `add_page_mode` is set to
            `AddPageMode.REPLACE`. List of page indices that need to be replaced with the given ones.
            Must represent a list of consecutive indices. Defaults to [].

        Returns:
            TableDetectorWorkspace: instance of self
        """
        
        if add_pages_numbers == 'all':
            pages = pdf_file.pages
        else:
            # then we assume add_pages_numbers is a list of indices
            
            if all(map(lambda i: 0 <= i < len(pdf_file.pages), add_pages_numbers)):
                pages = [pdf_file.pages[i] for i in add_pages_numbers]
            else:
                raise ValueError(f'Required: 0 <= add_pages_numbers < {len(self.pdf_file.pages)}, got add_pages_numbers={add_pages_numbers}')
            
        self.add_pages(
            pages,
            add_page_mode=add_page_mode,
            insert_after_page_number=insert_after_page_number,
            replace_page_numbers=replace_page_numbers
        )
        
        return self
    
    ###########################
    #        GET PAGES        #
    ###########################
    
    def get_page_object(self, page_number: int) -> page.Page:
        return self.pdf_file.pages[page_number].page
    
    def get_page_wrapper(self, page_number: int) -> PDFPageWrapper:
        return self.pdf_file.pages[page_number]
    
    def get_page_text(self, page_number: int) -> str:
        return self.pdf_file.pages[page_number].page.extract_text()
    
    def get_pages_objects(self, page_numbers: list[int]) -> list[page.Page]:
        return [self.pdf_file.pages[i].page for i in page_numbers]
    
    def get_pages_wrappers(self, page_numbers: list[int]) -> list[PDFPageWrapper]:
        return [self.pdf_file.pages[i] for i in page_numbers]
    
    def get_pages_text(self, page_numbers: list[int], *, merge: bool = False, delimiter: str = '\n') -> list[str] | str:
        txt_list = [self.pdf_file.pages[i].page.extract_text() for i in page_numbers]
        if merge:
            return delimiter.join(txt_list)
        else:
            return txt_list 
    
    @property
    def all_pages_objects(self) -> list[page.Page]:
        return [p.page for p in self.pdf_file.pages]
    
    def get_all_pages_text(self, *, merge: bool = False, delimiter: str = '\n') -> list[str] | str:
        txt_list = [p.page.extract_text() for p in self.pdf_file.pages]
        if merge:
            return delimiter.join(txt_list)
        else:
            return txt_list
    
    @property
    def pdf_file_wrapper(self) -> PDFFileWrapper:
        return self.pdf_file
    
    ###########################
    #      IMAGE WRAPPER      #
    ###########################
    
    def _get_pages_images_bytes(
        self,
        page_indices: list[int],
        resolution: int,
        *,
        antialias: bool = False,
        _format: str = 'PNG'
    ) -> list[bytes]:
        """
        Args:
            `page_indices (list[int])`: Indices of pages to extract the images from\n
            `resolution (int)`: resolution of the image extracted from the page.\n
            `antialias (bool, optional)`: Defaults to False.\n
            `_format (str, optional)`: Image formatting. Defaults to 'PNG'.\n

        Returns:
            `list[bytes]`: List of byte arrays - one for each image.
        """
        if isinstance(page_indices, list):
            if not all(map(lambda i: isinstance(i, int), page_indices)):
                raise TypeError('page_indices must be a list of integeres.')
        else:
            # my common mistake to give it one number instead of a list
            raise TypeError(f'page_indices must be a list. Got {type(page_indices)} instead.')
        
        img_bytes = []
        for i in page_indices:
            image_bytes_io = io.BytesIO()
            img = self.pdf_file.pages[i].page.to_image(resolution, antialias=antialias).debug_tablefinder(self.pdf_file.pages[i].table_settings)
            
            # quantize set to False cause otherwise it changes mode from RGB to P
            img.save(image_bytes_io, format=_format, quantize=False)
            
            img_bytes.append(image_bytes_io.getvalue())
            
        return img_bytes
    
    def set_pdf_file_image(
        self,
        page_indices: list[int] | Literal['all'] = 'all',
        resolution: int = BASE_IMAGE_RESOLUTION,
        antialias: bool = False,
        _format: str = 'PNG',
    ) -> 'TableDetectorWorkspace':
        
        self.logger.debug(f'Rendering images for {page_indices} pages with {resolution} px/in resolution, antialias {"on" if antialias else "off"} and format set to {_format}.')
        
        self.pdf_file.image = ImageWrapper(
            image_bytes=self._get_pages_images_bytes(
                [*range(len(self.pdf_file.pages))] if page_indices == 'all' else page_indices,
                resolution,
                antialias=antialias,
                _format=_format
            ),
            page_indices=page_indices,
            resolution=resolution,
            _format=_format,
            antialias=antialias
        )
        return self
    
    @property
    def image_bytes(self) -> list[bytes]:
        
        self.logger.debug('Applying pages\' settings to corresponding images.')
        
        # 'refresh' the image
        self.pdf_file.image.image_bytes=self._get_pages_images_bytes(
            page_indices=[*range(len(self.pdf_file.pages))] if self.pdf_file.image.page_indices == 'all' else self.pdf_file.image.page_indices,
            resolution=self.pdf_file.image.resolution,
            antialias=self.pdf_file.image.antialias,
            _format=self.pdf_file.image._format
        )
        
        self.logger.debug(f'{self.pdf_file.image.page_indices} pages were affected.')
        
        return self.pdf_file.image.image_bytes
    
    ###########################
    #      REMOVE PAGES       #
    ###########################
    
    def remove_page(self, page_number: int) -> 'TableDetectorWorkspace':
        self.pdf_file.pages.pop(page_number)
        return self
    
    def remove_pages(self, page_numbers: list[int]) -> 'TableDetectorWorkspace':
        pages_to_remove = [self.pdf_file.pages[i] for i in page_numbers]
        for p in pages_to_remove:
            self.pdf_file.pages.remove(p)
        return self
    
    def remove_all_pages(self) -> 'TableDetectorWorkspace':
        self.pdf_file.pages = []
        return self
    
    ###########################
    #  REMOVE & ADD ELEMENTS  #
    ###########################
            
    def _normalise_position(self, pos: _typing.T_num) -> _typing.T_num:
        ratio = BASE_IMAGE_RESOLUTION / self.pdf_file.image.resolution
        return pos * ratio
    
    def add_line(
        self,
        pos: _typing.T_num,
        orientation: Literal['vertical', 'horizontal'],
        page_index: int
    ) -> tuple['TableDetectorWorkspace', str]:
        
        if self.pdf_file.image is not None:
                
            if orientation not in ['vertical', 'horizontal']:
                raise ValueError(f'Orientation must be either vertical or horizontal. Got {orientation} instead.')
                
            normalised_pos = self._normalise_position(pos)
            line = ExplicitLineData(normalised_pos, orientation)
            self.pdf_file.pages[page_index].explicit_lines.append(line)
            self.set_table_settings_val(page_index, f'explicit_{orientation}_lines', list(set([p.value for p in self.pdf_file.pages[page_index].explicit_lines])))
            
            return self, line.uuid
            
        else:
            raise ValueError('Image has not been set, therefore, the element cannot be added. ' \
                'Use set_table_settings() method to add the element instead.')
            
    def update_line_pos(
        self,
        uuid: str,
        pos: _typing.T_num,
        page_index: int
    ) -> 'TableDetectorWorkspace':
        if self.pdf_file.image is not None:
            
            line_index, line = [(i, p) for i, p in enumerate(self.pdf_file.pages[page_index].explicit_lines) if p.uuid == uuid][0]
            line.value = self._normalise_position(pos)
            self.pdf_file.pages[page_index].explicit_lines[line_index] = line
            self.set_table_settings_val(page_index, f'explicit_{line.orientation}_lines', list(set([p.value for p in self.pdf_file.pages[page_index].explicit_lines])))
            
        else:
            raise ValueError('Image has not been set, therefore, the element cannot be removed. ' \
                'Use set_table_settings() method to add the element instead.')
            
    def remove_line(
        self,
        uuid: str,
        page_index: int
    ) -> 'TableDetectorWorkspace':
        if self.pdf_file.image is not None:
            
            line = [p for p in self.pdf_file.pages[page_index].explicit_lines if p.uuid == uuid][0]
            self.pdf_file.pages[page_index].explicit_lines.remove(line)
            self.set_table_settings_val(page_index, f'explicit_{line.orientation}_lines', list(set([p.value for p in self.pdf_file.pages[page_index].explicit_lines])))
            
        else:
            raise ValueError('Image has not been set, therefore, the element cannot be removed. ' \
                'Use set_table_settings() method to add the element instead.')
                
    def add_lines(
        self,
        pos: list[_typing.T_num],
        orientation: Literal['vertical', 'horizontal'],
        page_index: int
    ) -> tuple['TableDetectorWorkspace', list[str]]:
        uuids: list[str] = []
        
        for p in pos:
            uuids.append(self.add_line(p, orientation, page_index)[1])
        
        return self, uuids
    
    def remove_lines(
        self,
        pos: list[_typing.T_num],
        orientation: Literal['vertical', 'horizontal'],
        page_index: int
    ) -> 'TableDetectorWorkspace':
        for p in pos:
            self.remove_line(p, orientation, page_index)
        
        return self
    
    def add_table(
        self,
        top_left: tuple[_typing.T_num, _typing.T_num],
        bottom_right: tuple[_typing.T_num, _typing.T_num],
        vlines: list[_typing.T_num],
        hlines: list[_typing.T_num],
        page_index: int
    ) -> tuple['TableDetectorWorkspace', list[str]]:
        
        (x0, y0), (x1, y1) = top_left, bottom_right
        
        uuids = [
            *self.add_lines([x0, x1, *vlines], 'vertical', page_index)[1],
            *self.add_lines([y0, y1, *hlines], 'horizontal', page_index)[1]
        ]
        
        for line in self.pdf_file.pages[page_index].explicit_lines:
            for line.uuid in uuids:
                line.is_part_of_table = True
        
        return self, uuids
    
    def remove_table(
        self,
        top_left: tuple[_typing.T_num, _typing.T_num],
        bottom_right: tuple[_typing.T_num, _typing.T_num],
        vlines: list[_typing.T_num],
        hlines: list[_typing.T_num],
        page_index: int
    ) -> 'TableDetectorWorkspace':
        
        (x0, y0), (x1, y1) = top_left, bottom_right
        self.remove_lines([x0, x1, *vlines], 'vertical', page_index)
        self.remove_lines([y0, y1, *hlines], 'horizontal', page_index)
        
        return self
    
    def remove_all_elements(self, page_index: int) -> 'TableDetectorWorkspace':
        
        self.pdf_file.pages[page_index].explicit_lines = []
        
        self.set_table_settings_val(page_index, f'explicit_vertical_lines', [])
        self.set_table_settings_val(page_index, f'explicit_horizontal_lines', [])
        
        return self
    
    ###########################
    #    SET & GET SETTINGS   #
    ###########################
    
    def set_table_settings_val(self, page_index: int | list[int] | Literal['all'], key: str, val: Any) -> 'TableDetectorWorkspace':

        if isinstance(page_index, int):
            _p_ind = [page_index]
        elif isinstance(page_index, list):
            _p_ind = page_index
        elif page_index == 'all':
            _p_ind = self.pdf_file.image.page_indices if isinstance(self.pdf_file.image.page_indices, list) else [*range(len(self.pdf_file.pages))]
        else:
            raise TypeError
        
        for i in _p_ind:
        
            ts = self.get_table_settings(i)
            
            if key in ['explicit_vertical_lines', 'explicit_horizontal_lines']:
                
                bad_val_error_msg = 'Parameter val can be a list of numbers or a number when key is ' \
                    '\'explicit_vertical_lines\' or \'explicit_horizontal_lines\'.'
                
                if isinstance(val, list):
                    ts[key] = val
                elif isinstance(val, int):
                    if key in ts.keys():
                        if val not in ts[key]:
                            ts[key].append(val)
                    else:
                        ts[key] = [val]
                else:
                    raise ValueError(bad_val_error_msg)
                
                self.pdf_file.pages[i].table_settings = ts
            
            else:
                self.pdf_file.pages[i].table_settings[key] = val
        
        return self
        
    def get_table_settings(self, page_index: int) -> TypedObservableDict:
        return self.pdf_file.pages[page_index].table_settings
    
    ###########################
    #   GET TABLE TEXT DATA   #
    ###########################
    
    def get_tables_text(self, page_numbers: list[int]) -> list[list[list[str | None]]]:
        tables_text = []
        for i in page_numbers:
            tables_text += self.pdf_file.pages[i].page.extract_tables(self.pdf_file.pages[i].table_settings)
        return tables_text
    
    def get_all_tables_text(self) -> list[list[list[str | None]]]:
        return self.get_tables_text([i for i in range(len(self.pdf_file.pages))])
