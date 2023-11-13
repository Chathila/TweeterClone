### Description:
This project was undertaken to merge the practical aspects of software engineering with the theoretical understanding of databases. The goal was to demonstrate the relationship between a host programming language, in this case, Python, and SQL for managing and manipulating a database system, encapsulated within a social media context. The application simulates a blogging platform, allowing users to perform operations similar to Twitter. Users can log in or sign up, search for tweets or users using specific keywords, post tweets, and manage a list of followers. The search functionality offers paginated results and the ability to follow users directly from the search output. By implementing this project, I gained hands-on experience with SQL database interactions and user session management and developing a user-friendly command-line interface. 
### Testing:
To run the program:
- From the command line:
```shell
$ python3 main.py (optional) database_filename
```
where database_filename is the filename of the database in the current working directory the program will use. If none is specified, the test1.db database will be used. The file test1.db is the database I used to test to ensure proper functionality of the functions I implemented

### Dependencies:
The following libraries are required to run the program:
- sqlite3
- getpass
- datetime
- re
- math

If not installed on your system, run:
```shell
$ pip install (dependency_name)
``` 

