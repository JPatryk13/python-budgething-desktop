import io
from pathlib import Path
import unittest

from pdfplumber import open as pdf_open
from PIL import Image

from budgeting_app.pdf_table_reader.core.usecases.table_detector_workspace import TableDetectorWorkspace
from budgeting_app.pdf_table_reader.core.entities.models import PDFFileWrapper, PDFPageWrapper, BASE_IMAGE_RESOLUTION, ExplicitLineData


class TestTableDetectorWorkspace(unittest.TestCase):
    def setUp(self) -> None:
        
        self.test_data_path = Path(__file__).resolve().parent.parent.parent / 'data'
        
        self.multiple_pages_sample_pdf_filepath = self.test_data_path / 'multiple_pages_sample.pdf'
        
        self.multiple_pages_sample_pdf_file = pdf_open(self.multiple_pages_sample_pdf_filepath)
        
        # Elements only added here to distinguish between pages
        self.page0 = PDFPageWrapper(
            page=self.multiple_pages_sample_pdf_file.pages[0]
        )
        self.page1 = PDFPageWrapper(
            page=self.multiple_pages_sample_pdf_file.pages[1],
            explicit_lines=[ExplicitLineData(1, 'vertical')]
        )
        self.page2 = PDFPageWrapper(
            page=self.multiple_pages_sample_pdf_file.pages[2],
            explicit_lines=[ExplicitLineData(1, 'vertical'), ExplicitLineData(2, 'vertical')]
        )
        self.pdf_file_wrapper0 = PDFFileWrapper(pages=[self.page0, self.page1, self.page2])
        self.table_detector_workspace = TableDetectorWorkspace(self.pdf_file_wrapper0)
        
        self.single_page_sample_pdf_filepath = self.test_data_path / 'single_page_sample.pdf'
        
        self.single_page_sample_pdf_file = pdf_open(self.single_page_sample_pdf_filepath)
        
        # Data to use
        self.page3 = PDFPageWrapper(
            page=self.single_page_sample_pdf_file.pages[0],
            explicit_lines=[
                ExplicitLineData(1, 'vertical'),
                ExplicitLineData(2, 'vertical'),
                ExplicitLineData(3, 'vertical')
            ]
        )
        self.page4 = PDFPageWrapper(
            page=self.single_page_sample_pdf_file.pages[0],
            explicit_lines=[
                ExplicitLineData(1, 'vertical'),
                ExplicitLineData(2, 'vertical'),
                ExplicitLineData(3, 'vertical'),
                ExplicitLineData(4, 'vertical')
            ]
        )
        self.pdf_file_wrapper1 = PDFFileWrapper(pages=[self.page3, self.page4])
        
    def tearDown(self) -> None:
        self.multiple_pages_sample_pdf_file.close()
        self.single_page_sample_pdf_file.close()
        
    def test_create_table_detector(self) -> None:
        pdf_file_wrapper = PDFFileWrapper(pages=[])
        actual = TableDetectorWorkspace(pdf_file_wrapper)
        self.assertTrue(hasattr(actual, 'pdf_file'))
        self.assertEqual(actual.pdf_file, pdf_file_wrapper)
        self.assertEqual(actual.pdf_file.to_dict(), {'pages': [], 'image': None})

    ####################################
    #           ADD ONE PAGE           #
    ####################################

    def test_add_page_default_settings(self) -> None:
        expected = [self.page0, self.page1, self.page2, self.page3]
        actual = self.table_detector_workspace.add_page(self.page3).pdf_file.pages
        
        self.assertEqual(len(expected), len(actual))
        for p in expected:
            self.assertIn(p, actual)
        
    def test_add_page_add_page_mode_at_end(self) -> None:
        expected = [self.page0, self.page1, self.page2, self.page3]
        actual = self.table_detector_workspace.add_page(
            self.page3,
            add_page_mode=TableDetectorWorkspace.AddPageMode.AT_END
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)
    
    def test_add_page_add_page_mode_at_beggining(self) -> None:
        expected = [self.page3, self.page0, self.page1, self.page2]
        actual = self.table_detector_workspace.add_page(
            self.page3,
            add_page_mode=TableDetectorWorkspace.AddPageMode.AT_BEGGINING
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_page_add_page_mode_insert_after(self) -> None:
        expected = [self.page0, self.page3, self.page1, self.page2]
        actual = self.table_detector_workspace.add_page(
            self.page3,
            add_page_mode=TableDetectorWorkspace.AddPageMode.INSERT_AFTER,
            insert_after_page_number=0
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_page_add_page_mode_replace_one_page(self) -> None:
        expected = [self.page3, self.page1, self.page2]
        actual = self.table_detector_workspace.add_page(
            self.page3,
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_page_add_page_mode_replace_two_pages(self) -> None:
        expected = [self.page3, self.page2]
        actual = self.table_detector_workspace.add_page(
            self.page3,
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0, 1]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_page_add_page_mode_replace_all_pages(self) -> None:
        expected = [self.page3]
        actual = self.table_detector_workspace.add_page(
            self.page3,
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0, 1, 2]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)
        
    ####################################
    #         ADD MULTIPLE PAGE        #
    ####################################
        
    def test_add_pages_default_settings(self) -> None:
        expected = [self.page0, self.page1, self.page2, self.page3, self.page4]
        actual = self.table_detector_workspace.add_pages([self.page3, self.page4]).pdf_file.pages
        
        self.assertEqual(len(expected), len(actual))
        for p in expected:
            self.assertIn(p, actual)
        
    def test_add_pages_add_page_mode_at_end(self) -> None:
        expected = [self.page0, self.page1, self.page2, self.page3, self.page4]
        actual = self.table_detector_workspace.add_pages(
            [self.page3, self.page4],
            add_page_mode=TableDetectorWorkspace.AddPageMode.AT_END
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)
    
    def test_add_pages_add_page_mode_at_beggining(self) -> None:
        expected = [self.page3, self.page4, self.page0, self.page1, self.page2]
        actual = self.table_detector_workspace.add_pages(
            [self.page3, self.page4],
            add_page_mode=TableDetectorWorkspace.AddPageMode.AT_BEGGINING
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_pages_add_page_mode_insert_after(self) -> None:
        expected = [self.page0, self.page3, self.page4, self.page1, self.page2]
        actual = self.table_detector_workspace.add_pages(
            [self.page3, self.page4],
            add_page_mode=TableDetectorWorkspace.AddPageMode.INSERT_AFTER,
            insert_after_page_number=0
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_pages_add_page_mode_replace_one_page(self) -> None:
        expected = [self.page3, self.page4, self.page1, self.page2]
        actual = self.table_detector_workspace.add_pages(
            [self.page3, self.page4],
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0]
        ).pdf_file.pages
        
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_add_pages_add_page_mode_replace_two_pages(self) -> None:
        expected = [self.page3, self.page4, self.page2]
        actual = self.table_detector_workspace.add_pages(
            [self.page3, self.page4],
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0, 1]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_pages_add_page_mode_replace_all_pages(self) -> None:
        expected = [self.page3, self.page4]
        actual = self.table_detector_workspace.add_pages(
            [self.page3, self.page4],
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0, 1, 2]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)
        
    ####################################
    #        ADD PAGES FROM FILE       #
    ####################################
    
    def test_add_pages_from_file_default_settings(self) -> None:
        expected = [self.page0, self.page1, self.page2, *self.pdf_file_wrapper1.pages]
        actual = self.table_detector_workspace.add_pages_from_file(self.pdf_file_wrapper1).pdf_file.pages
        
        self.assertEqual(len(expected), len(actual))
        for p in expected:
            self.assertIn(p, actual)
        
    def test_add_pages_from_file_add_page_mode_at_end(self) -> None:
        expected = [self.page0, self.page1, self.page2, *self.pdf_file_wrapper1.pages]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_page_mode=TableDetectorWorkspace.AddPageMode.AT_END
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)
    
    def test_add_pages_from_file_add_page_mode_at_beggining(self) -> None:
        expected = [*self.pdf_file_wrapper1.pages, self.page0, self.page1, self.page2]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_page_mode=TableDetectorWorkspace.AddPageMode.AT_BEGGINING
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_pages_from_file_add_page_mode_insert_after(self) -> None:
        expected = [self.page0, *self.pdf_file_wrapper1.pages, self.page1, self.page2]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_page_mode=TableDetectorWorkspace.AddPageMode.INSERT_AFTER,
            insert_after_page_number=0
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_pages_from_file_add_page_mode_replace_one_page(self) -> None:
        expected = [*self.pdf_file_wrapper1.pages, self.page1, self.page2]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_pages_from_file_add_page_mode_replace_two_pages(self) -> None:
        expected = [*self.pdf_file_wrapper1.pages, self.page2]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0, 1]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)

    def test_add_pages_from_file_add_page_mode_replace_all_pages(self) -> None:
        expected = self.pdf_file_wrapper1.pages
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_page_mode=TableDetectorWorkspace.AddPageMode.REPLACE,
            replace_page_numbers=[0, 1, 2]
        ).pdf_file.pages
        
        self.assertEqual(expected, actual)
        
    def  test_add_pages_from_file_one_page(self) -> None:
        expected = [self.page0, self.page1, self.page2, self.page3]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_pages_numbers=[0]
        ).pdf_file.pages
        
        self.assertEqual(len(expected), len(actual))
        for p in expected:
            self.assertIn(p, actual)

    def  test_add_pages_from_file_two_pages(self) -> None:
        expected = [self.page0, self.page1, self.page2, self.page3, self.page4]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_pages_numbers=[0, 1]
        ).pdf_file.pages
        
        self.assertEqual(len(expected), len(actual))
        for p in expected:
            self.assertIn(p, actual)

    def  test_add_pages_from_file_all_pages_literal(self) -> None:
        expected = [self.page0, self.page1, self.page2, self.page3, self.page4]
        actual = self.table_detector_workspace.add_pages_from_file(
            self.pdf_file_wrapper1,
            add_pages_numbers='all'
        ).pdf_file.pages
        
        self.assertEqual(len(expected), len(actual))
        for p in expected:
            self.assertIn(p, actual)

    ####################################
    #         GET PAGE OBJECTS         #
    ####################################
    
    def test_get_page_obj(self) -> None:
        expected = self.page0.page
        actual = self.table_detector_workspace.get_page_object(0)
        self.assertEqual(expected, actual)

    def test_get_page_objs(self) -> None:
        expected = [self.page0.page, self.page1.page]
        actual = self.table_detector_workspace.get_pages_objects([0, 1])
        self.assertEqual(expected, actual)

    def test_get_all_page_objs(self) -> None:
        expected = [self.page0.page, self.page1.page, self.page2.page]
        actual = self.table_detector_workspace.all_pages_objects
        self.assertEqual(expected, actual)

    ####################################
    #         GET PAGE WRAPPERS        #
    ####################################
    
    def test_get_page_wrapper(self) -> None:
        expected = self.page0
        actual = self.table_detector_workspace.get_page_wrapper(0)
        self.assertEqual(expected, actual)

    def test_get_page_wrappers(self) -> None:
        expected = [self.page0, self.page1]
        actual = self.table_detector_workspace.get_pages_wrappers([0, 1])
        self.assertEqual(expected, actual)
    
    ####################################
    #           GET PAGE TEXT          #
    ####################################
    
    def test_get_page_text(self) -> None:
        expected = self.page0.page.extract_text()
        actual = self.table_detector_workspace.get_page_text(0)
        self.assertEqual(expected, actual)

    def test_get_pages_text(self) -> None:
        expected = [
            self.page0.page.extract_text(),
            self.page1.page.extract_text()
        ]
        actual = self.table_detector_workspace.get_pages_text([0, 1])
        self.assertEqual(expected, actual)

    def test_get_all_pages_text(self) -> None:
        expected = [
            self.page0.page.extract_text(),
            self.page1.page.extract_text(),
            self.page2.page.extract_text()
        ]
        actual = self.table_detector_workspace.get_all_pages_text()
        self.assertEqual(expected, actual)

    def test_get_pages_text_merge_default_delimiter(self) -> None:
        expected = '\n'.join([
            self.page0.page.extract_text(),
            self.page1.page.extract_text()
        ])
        actual = self.table_detector_workspace.get_pages_text([0, 1], merge=True)
        self.assertEqual(expected, actual)

    def test_get_all_pages_text_merge_default_delimiter(self) -> None:
        expected = '\n'.join([
            self.page0.page.extract_text(),
            self.page1.page.extract_text(),
            self.page2.page.extract_text()
        ])
        actual = self.table_detector_workspace.get_all_pages_text(merge=True)
        self.assertEqual(expected, actual)
        
    def test_get_pages_text_merge_custom_delimiter(self) -> None:
        expected = ' '.join([
            self.page0.page.extract_text(),
            self.page1.page.extract_text()
        ])
        actual = self.table_detector_workspace.get_pages_text([0, 1], merge=True, delimiter=' ')
        self.assertEqual(expected, actual)

    def test_get_all_pages_text_merge_custom_delimiter(self) -> None:
        expected = ' '.join([
            self.page0.page.extract_text(),
            self.page1.page.extract_text(),
            self.page2.page.extract_text()
        ])
        actual = self.table_detector_workspace.get_all_pages_text(merge=True, delimiter=' ')
        self.assertEqual(expected, actual)
    
    ####################################
    #         GET FILE WRAPPER         #
    ####################################
    
    def test_get_file_wrapper(self) -> None:
        expected = self.pdf_file_wrapper0
        actual = self.table_detector_workspace.pdf_file_wrapper
        self.assertEqual(expected, actual)
    
    ####################################
    #           REMOVE PAGES           #
    ####################################

    def test_remove_page(self) -> None:
        expected = [self.page0, self.page2]
        actual = self.table_detector_workspace.remove_page(1).pdf_file.pages
        self.assertEqual(expected, actual)

    def test_remove_pages(self) -> None:
        expected = [self.page0]
        self.table_detector_workspace.pdf_file.pages
        actual = self.table_detector_workspace.remove_pages([1, 2]).pdf_file.pages
        self.assertEqual(expected, actual)

    def test_remove_all_pages(self) -> None:
        expected = []
        actual = self.table_detector_workspace.remove_all_pages().pdf_file.pages
        self.assertEqual(expected, actual)
        
    ####################################
    #          IMAGE WRAPPER           #
    ####################################
    
    def test__get_page_image_bytes(self) -> None:
        expected_img = self.page0.page.to_image(BASE_IMAGE_RESOLUTION).original
        actual_bytes = self.table_detector_workspace._get_pages_images_bytes([0], BASE_IMAGE_RESOLUTION)
        actual_img = list(map(lambda b: Image.open(io.BytesIO(b)), actual_bytes))
        self.assertTrue(isinstance(actual_bytes, list))
        self.assertEqual(len(actual_bytes), 1)
        self.assertEqual(expected_img.mode, actual_img[0].mode)
        self.assertEqual(expected_img.size, actual_img[0].size)

    def test__get_pages_images_bytes(self) -> None:
        resolution = 200
        expected_img_list = [self.page0.page.to_image(resolution).original, self.page1.page.to_image(resolution).original]
        actual_bytes_list = self.table_detector_workspace._get_pages_images_bytes([0, 1], resolution)
        actual_img_list = [Image.open(io.BytesIO(actual_bytes_list[0])), Image.open(io.BytesIO(actual_bytes_list[1]))]
        
        # Check the type and size of actual_bytes_list
        self.assertTrue(isinstance(actual_bytes_list, list))
        self.assertEqual(len(actual_bytes_list), 2)
        self.assertTrue(isinstance(actual_bytes_list[0], bytes) and isinstance(actual_bytes_list[1], bytes))
        
        # Check the properties of each img
        self.assertEqual(expected_img_list[0].mode, actual_img_list[0].mode)
        self.assertEqual(expected_img_list[0].size, actual_img_list[0].size)
        self.assertEqual(expected_img_list[1].mode, actual_img_list[1].mode)
        self.assertEqual(expected_img_list[1].size, actual_img_list[1].size)
    
    def test_set_pdf_file_image_one_page_image(self) -> None:
        expected = self.table_detector_workspace.pdf_file.pages[0].page.to_image(BASE_IMAGE_RESOLUTION).original
        self.table_detector_workspace.set_pdf_file_image(page_indices=[0])
        
        # check if the image has been created correctly
        self.assertTrue(self.table_detector_workspace.pdf_file.image is not None)
        self.assertEqual(len(self.table_detector_workspace.pdf_file.image.image_bytes), 1)
        self.assertEqual(self.table_detector_workspace.pdf_file.image.page_indices, [0])
        self.assertEqual(self.table_detector_workspace.pdf_file.image.resolution, BASE_IMAGE_RESOLUTION)
        self.assertEqual(self.table_detector_workspace.pdf_file.image._format, 'PNG')
        self.assertEqual(self.table_detector_workspace.pdf_file.image.antialias, False)
        
        actual_img = Image.open(io.BytesIO(self.table_detector_workspace.pdf_file.image.image_bytes[0]))
        
        # check the properties of the image
        self.assertEqual(expected.mode, actual_img.mode)
        self.assertEqual(expected.size, actual_img.size)

    def test_set_pdf_file_image_all_pages(self) -> None:
        expected = [p.page.to_image(BASE_IMAGE_RESOLUTION).original for p in self.table_detector_workspace.pdf_file.pages]
        self.table_detector_workspace.set_pdf_file_image()
        
        # check if the images has been created correctly
        self.assertTrue(self.table_detector_workspace.pdf_file.image is not None)
        self.assertEqual(len(self.table_detector_workspace.pdf_file.image.image_bytes), 3)
        self.assertEqual(self.table_detector_workspace.pdf_file.image.page_indices, 'all')
        self.assertEqual(self.table_detector_workspace.pdf_file.image.resolution, BASE_IMAGE_RESOLUTION)
        self.assertEqual(self.table_detector_workspace.pdf_file.image._format, 'PNG')
        self.assertEqual(self.table_detector_workspace.pdf_file.image.antialias, False)
        
        actual_img = [Image.open(io.BytesIO(b)) for b in self.table_detector_workspace.pdf_file.image.image_bytes]
        
        # check the properties of each image
        for e, a in zip(expected, actual_img):
            self.assertEqual(e.mode, a.mode)
            self.assertEqual(e.size, a.size)
        

    def test_set_pdf_file_image_high_resolution(self) -> None:
        expected = self.table_detector_workspace.pdf_file.pages[0].page.to_image(1000).original
        self.table_detector_workspace.set_pdf_file_image(page_indices=[0], resolution=1000)
        
        # check if the image has been created correctly
        self.assertTrue(self.table_detector_workspace.pdf_file.image is not None)
        self.assertEqual(len(self.table_detector_workspace.pdf_file.image.image_bytes), 1)
        
        actual_img = Image.open(io.BytesIO(self.table_detector_workspace.pdf_file.image.image_bytes[0]))
        
        # check the properties of the image
        self.assertEqual(expected.mode, actual_img.mode)
        self.assertEqual(expected.size, actual_img.size)
        self.assertEqual(self.table_detector_workspace.pdf_file.image.resolution, 1000)

    ####################################
    #       ADD & REMOVE ELEMENTS      #
    ####################################
    
    def tast_add_line_vertical(self) -> None:
        expected = 100
        self.table_detector_workspace.set_pdf_file_image().add_line(expected, 'vertical', 0)
        self.assertIn('explicit_vertical_lines', self.table_detector_workspace.pdf_file.pages[0].table_settings)
        self.assertIn(expected, self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'])

    def tast_add_line_horizontal(self) -> None:
        expected = 100
        self.table_detector_workspace.set_pdf_file_image().add_line(expected, 'horizontal', 0)
        self.assertIn('explicit_horizontal_lines', self.table_detector_workspace.pdf_file.pages[0].table_settings)
        self.assertIn(expected, self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'])
        
    def test_add_line_that_exists(self) -> None:
        pos = 100
        self.table_detector_workspace.set_pdf_file_image().add_line(pos, 'horizontal', 0)[0].add_line(pos, 'horizontal', 0)
        self.assertIn(pos, self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'])
        self.assertEqual(len(list(filter(lambda p: p == pos, self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines']))), 1)
        
    def tast_remove_line_vertical(self) -> None:
        pos = 100
        self.table_detector_workspace.set_pdf_file_image().add_line(pos, 'vertical', 0).remove_line(pos, 'vertical', 0)
        self.assertNotIn(pos, self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'])

    def tast_remove_line_horizontal(self) -> None:
        pos = 100
        self.table_detector_workspace.set_pdf_file_image().add_line(pos, 'horizontal', 0).remove_line(pos, 'horizontal', 0)
        self.assertNotIn(pos, self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'])

    def tast_add_lines_vertical(self) -> None:
        expected = [100, 200]
        self.table_detector_workspace.set_pdf_file_image().add_lines(expected, 'vertical', 0)
        self.assertIn('explicit_vertical_lines', self.table_detector_workspace.pdf_file.pages[0].table_settings)
        self.assertIn(expected[0], self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'])
        self.assertIn(expected[1], self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'])
 
    def tast_add_lines_horizontal(self) -> None:
        expected = [100, 200]
        self.table_detector_workspace.set_pdf_file_image().add_lines(expected, 'horizontal', 0)
        self.assertIn('explicit_horizontal_lines', self.table_detector_workspace.pdf_file.pages[0].table_settings)
        self.assertIn(expected[0], self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'])
        self.assertIn(expected[1], self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'])

    def tast_add_table(self) -> None:
        expected = {
            'explicit_vertical_lines': [10, 90, 170, 250],
            'explicit_horizontal_lines': [10, 170, 250]
        }
        self.table_detector_workspace.set_pdf_file_image().add_table((10, 10), (250, 250), [90, 170], [130], 0)
        for k, v in expected.items():
            self.assertIn(k, self.table_detector_workspace.pdf_file.pages[0].table_settings)
            for pos in v:
                self.assertIn(pos, self.table_detector_workspace.pdf_file.pages[0].table_settings[k])

    def tast_remove_table(self) -> None:
        self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'] = [10, 90, 170, 250]
        self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'] = [10, 170, 250]
        self.table_detector_workspace.set_pdf_file_image().remove_table((10, 10), (250, 250), [90, 170], [130], 0)
        self.assertEqual(self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'], [])
        self.assertEqual(self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'], [])

    def test_remove_all_elements(self) -> None:
        self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'] = [10, 20, 30]
        self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'] = [30, 40, 50]
        self.table_detector_workspace.remove_all_elements(0)
        self.assertEqual(self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_vertical_lines'], [])
        self.assertEqual(self.table_detector_workspace.pdf_file.pages[0].table_settings['explicit_horizontal_lines'], [])

    ####################################
    #     SET & GET TABLE SETTINGS     #
    ####################################
    
    def test_set_table_settings(self) -> None:
        settings = {
            "vertical_strategy": "explicit",
            "explicit_vertical_lines": [55],
            "snap_tolerance": 5,
            "join_tolerance": 1,
        }
        for k, v in settings.items():
            self.table_detector_workspace.set_table_settings_val(0, k, v)
        
        actual = self.table_detector_workspace.pdf_file.pages[0].table_settings
        
        for k, v in settings.items():
            self.assertIn(k, actual.keys())
            self.assertEqual(v, actual[k])
        
    
    def test_set_table_settings_with_existing_settings(self) -> None:
        existing_settings = {
            "vertical_strategy": "explicit",
            "explicit_vertical_lines": [55],
        }
        new_settings = {
            "snap_tolerance": 5,
            "join_tolerance": 1,
        }
        self.table_detector_workspace.pdf_file.pages[0].table_settings = existing_settings
        
        for k, v in new_settings.items():
            self.table_detector_workspace.set_table_settings_val(0, k, v)
            
        actual = self.table_detector_workspace.pdf_file.pages[0].table_settings
        
        for k, v in {**existing_settings, **new_settings}.items():
            self.assertIn(k, actual.keys())
            self.assertEqual(v, actual[k])

    def test_get_table_settings(self) -> None:
        settings = {
            "vertical_strategy": "explicit",
            "explicit_vertical_lines": [55],
            "snap_tolerance": 5,
            "join_tolerance": 1,
        }
        self.table_detector_workspace.pdf_file.pages[0].table_settings = settings
        actual = self.table_detector_workspace.get_table_settings(0)
        
        for k, v in settings.items():
            self.assertIn(k, actual.keys())
            self.assertEqual(v, actual[k])

    ####################################
    #       GET TABLE TEXT DATA        #
    ####################################
    
    def test_get_tables_text_single_table(self) -> None:
        pdf_file = pdf_open(self.test_data_path / '1_table_1_page.pdf')
        page0 = pdf_file.pages[0].debug_tablefinder().page
        expected = [[['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']]]
        actual = TableDetectorWorkspace(PDFFileWrapper([PDFPageWrapper(page0)])).get_tables_text([0])
        pdf_file.close()
        self.assertEqual(expected, actual)

    def test_get_tables_text_two_tables(self) -> None:
        pdf_file = pdf_open(self.test_data_path / '2_tables_1_page.pdf')
        page0 = pdf_file.pages[0].debug_tablefinder().page
        expected = [
            [['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']],
            [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        ]
        actual = TableDetectorWorkspace(PDFFileWrapper([PDFPageWrapper(page0)])).get_tables_text([0])
        pdf_file.close()
        self.assertEqual(expected, actual)

    def test_get_all_tables_text(self) -> None:
        pdf_file = pdf_open(self.test_data_path / '3_tables_2_pages.pdf')
        page0 = pdf_file.pages[0].debug_tablefinder().page
        page1 = pdf_file.pages[1].debug_tablefinder().page
        expected = [
            [['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']],
            [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']],
            [['X1', 'X2', 'X3'], ['X4', 'X5', 'X6'], ['X7', 'X8', 'X9']]
        ]
        actual = TableDetectorWorkspace(PDFFileWrapper([PDFPageWrapper(page0), PDFPageWrapper(page1)])).get_all_tables_text()
        pdf_file.close()
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()