import sqlite3
import sys
from options import print_main_menu, compose, list_followers, search_user, search_tweet
from login import print_login_menu, get_input, signup_user, login_user, logout_user, post_login

connection, cursor = None, None

def connect(path):
    """
    Create the connection object, cursor, and enforce foreign key constraints.
    @param path: relative file path to database.
    """
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute( "PRAGMA foreign_keys=ON;" )

    connection.commit()

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "./test1.db"
    connect(path)

    user = None
    loggedIn = False
    programQuit = False
    
    while not programQuit:
        if not loggedIn:
            while not loggedIn:
                print_login_menu()
                select = get_input(['a', 'b', 'q'])
                match select:
                    case 'a':
                        # Signup
                        signup_user(connection, cursor)
                    case 'b':
                        # Login
                        loggedIn, user = login_user(cursor)
                        if loggedIn:
                            post_login(connection, cursor, user)
                    case 'q':
                        # Quit Program
                        programQuit = True
                        break
        else:
            while loggedIn:
                print_main_menu()
                select = get_input(['t', 'u', 'c', 'l', 'q'])
                match select:
                    case 't':
                        # Search for Tweets
                        search_tweet(cursor, connection, user, get_input)
                    case 'u':
                        # Search for Users
                        search_user(cursor,connection,user)
                    case 'c':
                        # Compose a Tweet
                        compose(cursor,connection,user)
                    case 'l':
                        # List Followers
                        list_followers(connection, cursor, user)
                    case 'q':
                        loggedIn, user = logout_user(user)                  


if __name__ == "__main__":
    main()