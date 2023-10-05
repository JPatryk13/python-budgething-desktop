# BDD - Features
## Drag and drop a file
> As the user of the app,
> I want to drag and drop a file
> and be informed by the interface behaviour if the file is acceptable by the app before I drop it
> and when I drop the acceptable file I want an appropriate - to the file type - window to be open.
> If the file is not acceptable I want no special behaviour from the interface
## Manual table extraction

> As the user of the app
> I want to be able to use the graphic interface to navigate the images of the PDF pages
> and draw tables which will mark the data as in-table and be automatically extracted.
> I want to modify and delete the tables created by me.
> I want the tables to not affect eachother.

### Definitions:
*hand tool* 
: allows you to manipulate the image itself and drawn tables

*table tool*
: allows you to draw tables

*added lines*
: vertical and horizontal lines that are manually added by using the RHS toolbox

*settings*
: the advanced options that influence how pdfplumber detects tables

*strategy*
: options that influence what pdfplumber uses to detect tables - drawn lines, detected lines, text, etc.

*added to the image*
: added to the gui representation of the image

*applied to the image*
: added to the image render via pdfplumber

### Notes:
Sub-features, here, are marked by tags ending with .feature.

- hand_tool.feature
- table_tool.feature
- drawing.feature
- tabs.feature
- toolbox.feature
- table_detection.feature
