Feature: Drag and drop a file

    As the user of the app,
    I want to drag and drop a file
    and be informed by the interface behaviour if the file is acceptable by the app before I drop it
    and when I drop the acceptable file I want an appropriate - to the file type - window to be open.
    If the file is not acceptable I want no special behaviour from the interface

    Scenario Outline: I want the AddDataFromFile window to 'tell me' if file-type is acceptable
        Given I have the "AddDataFromFile" window open
        And I have a valid <filename> file
        When I drag the file
        Then I see that it is <is_acceptable> filetype
        Examples:
            | filename    | is_acceptable  |
            | sample.pdf  | acceptable     |
            | sample.csv  | acceptable     |
            | sample.json | acceptable     |
            | sample.txt  | not acceptable |
            | sample.png  | not acceptable |
            | sample.docx | not acceptable |

    Scenario Outline: I want the AddDataFromFile window to accept only the acceptable filetypes and ignore the rest
        Given I have the "AddDataFromFile" window open
        And I have a valid <filename> file
        When I drag and drop the file
        Then The file is <is_accepted>
        Examples:
            | filename    | is_accepted  |
            | sample.pdf  | accepted     |
            | sample.csv  | accepted     |
            | sample.json | accepted     |
            | sample.txt  | not accepted |
            | sample.png  | not accepted |
            | sample.docx | not accepted |

    Scenario Outline: I want the AddDataFromFile window to open relevant window depending on the file type
        Given I have the "AddDataFromFile" window open
        And I have a valid <filename> file
        When I drag and drop the file
        Then The file is <is_accepted>
        And <service_name> is opened
        Examples:
            | filename    | is_accepted | service_name       |
            | sample.pdf  | accepted    | TableExtractor     |
            | sample.csv  | accepted    | CSVTableExtractor  |
            | sample.json | accepted    | JSONTableExtractor |

    Scenario: I want the TableExtractor to immedietaly detect a simple table when the file is dropped
        Given I have the "AddDataFromFile" window open
        And I have a valid 1_table_1_page.pdf file
        And the data are
            | A | B | C |
            | D | E | F |
            | G | H | I |
        When I drag and drop the file
        Then TableExtractor is opened
        And the number of displayed tabs is 1
        And I can see my data in the table widget

    Scenario: I want the TableExtractor to immedietaly detect and merge multiple simple tables when the file is dropped
        Given I have the "AddDataFromFile" window open
        And I have a valid 2_tables_1_page.pdf file
        And the data are
            | A | B | C |
            | D | E | F |
            | G | H | I |
            | 1 | 2 | 3 |
            | 4 | 5 | 6 |
            | 7 | 8 | 9 |
        When I drag and drop the file
        Then TableExtractor is opened
        And the number of displayed tabs is 1
        And I can see my data in the table widget

    Scenario: I want the TableExtractor to immedietaly detect and merge multiple simple tables across multiple pages when the file is dropped
        Given I have the "AddDataFromFile" window open
        And I have a valid 3_tables_2_pages.pdf file
        And the data are
            | A  | B  | C  |
            | D  | E  | F  |
            | G  | H  | I  |
            | 1  | 2  | 3  |
            | 4  | 5  | 6  |
            | 7  | 8  | 9  |
            | X1 | X2 | X3 |
            | X4 | X5 | X6 |
            | X7 | X8 | X9 |
        When I drag and drop the file
        Then TableExtractor is opened
        And the number of displayed tabs is 2
        And I can see my data in the table widget

