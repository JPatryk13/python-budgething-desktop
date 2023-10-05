Feature: Manual table extraction

    As the user of the app
    I want to be able to use the graphic interface to navigate the images of the PDF pages
    and draw tables which will mark the data as in-table and be automatically extracted.
    I want to modify and delete the tables created by me.
    I want the tables to not affect eachother.

    ########################################
    #             IMAGE VIEWER             #
    ########################################

    @hand_tool.feature
    Scenario: Hand tool is ready to use as soon as the AddDataFromFile window is open
        Given I have a valid sample.pdf file
        And I have the "TableExtractor" window open
        Then the "hand tool" is selected

    @hand_tool.feature @slow @skip
    Scenario: Hand tool allows to move the image
        Given I have a valid sample.pdf file
        And I have the "TableExtractor" window open
        When I select the "hand tool"
        And I hold "left mouse button" and drag the coursor within "image viewer" from "centre" "to left"
        Then the image "moves with the coursor"
        When I release the "left mouse button"
        Then the image "remains in its position"

    @hand_tool.feature
    Scenario: Hand tool allows to scale the image
        Given I have a valid sample.pdf file
        And I have the "TableExtractor" window open
        When I select the "hand tool"
        And I move the mouse scroll "forward" within "image viewer"
        Then the image "becomes bigger"
        When I move the mouse scroll "backward" within "image viewer"
        Then the image "becomes smaller"

    @tabs.feature
    Scenario: Scale and position of the image is preserved even when I switch between tabs
    @drawing.feature @table_tool.feature
    Scenario: When table tool is selected holding left mouse button and moving the coursor causes a table to be drawn
    @drawing.feature @table_tool.feature
    Scenario: Releasing the left mouse button causes the table to be ADDED TO THE IMAGE (but not applied)
    @drawing.feature @table_tool.feature
    Scenario: Releasing the left mouse button causes the hand tool and the just-drawn table to be selected
    @drawing.feature @table_tool.feature
    Scenario: The table cannot be drawn below it's smallest dimensions
    @drawing.feature @hand_tool.feature
    Scenario: Clicking with hand tool on the edge of the table cause the table to be selected - handles appear around some of the table's edges
    @drawing.feature @hand_tool.feature
    Scenario: Clicking with left mouse button on the handle that is attached to the table line and dragging it causes the line to move
    @drawing.feature @hand_tool.feature
    Scenario: Clicking with left mouse button on the handle that is attached to the table boundary and dragging it causes the table to change size

    ########################################
    #        IMAGE VIEWER + TOOLBOX        #
    ########################################

    @hand_tool.feature @toolbox.feature
    Scenario: Clicking on the table causes its number of columns and rows to appear in the toolbox
    @hand_tool.feature @toolbox.feature
    Scenario: Clicking table tool when hand tool is selected causes any selected tables to deselect and the col/row count section of the toolbox to dissapear
    @drawing.feature @tabs.feature
    Scenario: Settings, added lines and drawn tables are preserved only within the page that I have currently selected

    ########################################
    #               TOOLBOX                #
    ########################################

    @tabs.feature @toolbox.feature
    Scenario: Settings and added lines are preserved in UI for each tab separately
    @toolbox.feature @table_detection.feature
    Scenario: Strategy is APPLIED TO THE IMAGE automatically when the user selects it
    @drawing.feature @toolbox.feature
    Scenario: Tables and added lines are ADDED TO THE IMAGE even if I won't press the find tables button
    @toolbox.feature @table_detection.feature
    Scenario: Settings, tables and added lines are APPLIED TO THE IMAGE only when I press the find tables button
    @table_detection.feature
    Scenario: Removing tables and added lines is not APPLIED TO THE IMAGE until I press the find tables button
    @toolbox.feature
    Scenario: Find tables button is disabled when no changes to the image or toolbox features is present

    ########################################
    #     IMAGE VIEWER + TABLE WIDGET      #
    ########################################

    @drawing.feature @table_detection.feature @table_widget.feature
    Scenario: When I draw a table on visibly separated data and press find tables button, I will see that data in the table widget
    @drawing.feature @table_detection.feature @table_widget.feature
    Scenario: When I remove only present table and press find tables button, I will see no table in the table widget
    @drawing.feature @table_detection.feature @table_widget.feature
    Scenario: When I draw multiple tables on visibly separated data on the same page and press find tables button, I will see that data aggregatet in the table widget
    @drawing.feature @table_detection.feature @table_widget.feature
    Scenario: When I remove one out of multiple tables (within one page), I will see the data is affected in the table widget
    @drawing.feature @table_detection.feature @table_widget.feature
    Scenario: When I draw multiple tables on visibly separated data on different pages and press find tables button, I will see that data aggregatet in the table widget
    @drawing.feature @table_detection.feature @table_widget.feature
    Scenario: When I remove one out of multiple tables (across different pages), I will see the data is affected in the table widget

    ########################################
    #             TABLE WIDGET             #
    ########################################

    @table_widget.feature
    Scenario: Names of the columns can be selected from a dropdown box and are the same as names of required fields in the model