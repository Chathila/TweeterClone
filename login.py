import getpass
from datetime import datetime
from options import build_tweet


def get_input(values):
    """
    Prompt the user for a menu selection. User input is checked against list of possible values.
    @param values: list of acceptable user input values, all lowercase if characters.
    """
    select = (input("Select: ")).lower()
    while select not in values:
        print("Invalid input. Please try again.")
        select = (input("Select: ")).lower()
    return select

def print_login_menu():
    """
    Print the LoginMenu for the Login Screen.
    """
    print("------------LOGIN SCREEN------------")
    print("------------------------------------")
    print("Options:  A - Signup")
    print("          B - Login")
    print("          Q - Quit Program")

def signup_user(connection, cursor):
    cursor.execute("""
                   SELECT MAX(usr)
                   FROM users;
                   """)
    newUserID = cursor.fetchone()
    if newUserID:
        newUserID = newUserID[0] + 1
    else:
        newUserID = 1

    print("---------------SignUp---------------")
    name = input("Enter your name: ")

    password1 = getpass.getpass("Enter your password: ")
    password2 = getpass.getpass("Repeat password: ")
    if password1 != password2:
        print("------------------------------------")
        print("Error: passwords do not match. Please try again.")
        print("------------------------------------")
        return
    
    email = input ("Enter your email: ")
    city = input ("Enter your city: ")
    timezone = input("Enter your timezone: ")
    
    cursor.execute("""
                   INSERT INTO users (usr, pwd, name, email, city, timezone) 
                   VALUES (?, ?, ?, ?, ?, ?);
                   """,(newUserID, password1, name, email, city, timezone))
    print("------------------------------------")
    print(f"Thank you for signing up, {name}! Your userID is {newUserID}.")
    print("------------------------------------")

    connection.commit()

def login_user(cursor):
    print("---------------Login----------------")
    userID = input("Enter your userID: ")
    password = getpass.getpass("Enter your password: ")

    cursor.execute("SELECT * FROM users WHERE usr = ? AND pwd = ?", (userID, password))
    
    user = cursor.fetchone()
    loggedIn = False

    if user:
        print("------------------------------------")
        print(f"Login successful, welcome {user[2]}!")
        print("------------------------------------")
        loggedIn = True
        return loggedIn, user
    else:
        print("------------------------------------")
        print("Login failed! Please recheck your credentials and try again.")
        print("------------------------------------")
        return loggedIn, user
    
def logout_user(user):
    print("------------------------------------")
    print(f"Logout successful, goodbye {user[2]}!")
    print("------------------------------------")
    
    user = None
    loggedIn = False
    return loggedIn, user

def post_login(connection, cursor, user):
    userID = user[0]
    cursor.execute("""
                   SELECT u.name, 'Tweet', t.tdate, t.text, t.tid, u.usr
                   FROM tweets t, follows f, users u
                   WHERE f.flwer = ? AND f.flwee = t.writer AND t.writer = u.usr
                   ORDER BY t.tdate DESC;
                   """, (userID,))
    tweetRows = cursor.fetchall()
    cursor.execute("""
                   SELECT u1.name, 'Retweet', rt.rdate, t.text, t.tid, u1.usr, u2.name, u2.usr
                   FROM retweets rt, tweets t, follows f, users u1, users u2
                   WHERE f.flwer = ? AND f.flwee = rt.usr AND u1.usr = rt.usr
                    AND rt.tid = t.tid AND t.writer = u2.usr
                   ORDER BY t.tdate DESC;
                   """, (userID,))
    retweetRows = cursor.fetchall()

    combinedRows = None
    if tweetRows and retweetRows:
        combinedRows = tweetRows + retweetRows
    elif tweetRows:
        combinedRows = tweetRows
    elif retweetRows:
        combinedRows = retweetRows

    print("-----------Recent Activity----------")
    if not combinedRows:
        print("You have no recent activity.")
    else:        
        combinedRows.sort(key=lambda a:a[2], reverse=True)
        index = 0
        stop = 5
        numRows = len(combinedRows)

        print("{0:^10} | {1:^25} | {2:^12} | {3:<50}".format( "#-Type", "Followee", "Date", "Text"))
        print("-------------------------------------------------------------------------")
        while index < numRows and index < stop:
            row = combinedRows[index]
            flwee = row[0]
            flweeID = row[5]
            flwee = f"(ID:{flweeID}) {flwee}"
            # if len(flwee) > 17:
            #     flwee = flwee[:17] + "..."
            if row[1] == "Tweet":
                print("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(str(index+1)+"-"+row[1], flwee, row[2], row[3]))
            else:
                ogWriter = row[6]
                ogWriterID = row[7]
                text = f"(From {ogWriter}@ID:{ogWriterID}) {row[3]}"
                print("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(str(index+1)+"-"+row[1], flwee, row[2], text))
            index += 1
        print("-------------------------------------------------------------------------")    
        print("Options:  M - More recent activity")
        print("          I - Tweet information")
        print("          R - Reply to tweet")
        print("          T - Retweet a tweet")
        print("          C - Continue to Main Menu")
        select = get_input(['m', 'i', 'r', 't', 'c'])
        while select != 'c':
            match select:
                case 'm':
                    print("-----------Recent Activity----------")
                    stop += 5
                    if index >= numRows:
                        print("You have no more recent activity.")
                        print("------------------------------------")
                    else:
                        print("{0:^10} | {1:^25} | {2:^12} | {3:<50}".format( "#-Type", "Followee", "Date", "Text"))
                        print("-------------------------------------------------------------------------")
                        while index < numRows and index < stop:
                            row = combinedRows[index]
                            flwee = row[0]
                            flweeID = row[5]
                            flwee = f"(ID:{flweeID}) {flwee}"
                            # if len(flwee) > 17:
                            #     flwee = flwee[:17] + "..."
                            if row[1] == "Tweet":
                                print("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(str(index+1)+"-"+row[1], flwee, row[2], row[3]))
                            else:
                                ogWriter = row[6]
                                ogWriterID = row[7]
                                text = f"(From {ogWriter}@ID:{ogWriterID}) {row[3]}"
                                print("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(str(index+1)+"-"+row[1], flwee, row[2], text))
                            index += 1
                        print("-------------------------------------------------------------------------")
                case 'i':
                    print("----------Tweet Information---------")
                    tweetNum = input("Select tweet number for information: ")
                    if tweetNum.isnumeric():
                        tweetNum = int(tweetNum)
                    else:
                        tweetNum = 0
                    if not (1 <= tweetNum <= index):
                        print("------------------------------------")
                        print("Invalid tweet selection.")
                        print("------------------------------------")
                    elif combinedRows[tweetNum-1][1] == 'Retweet':
                        print("------------------------------------")
                        print("There is no information about retweets.")
                        print("------------------------------------")
                    else:
                        row = combinedRows[tweetNum-1]
                        tweetID = row[4]
                        cursor.execute("""
                                       SELECT *
                                       FROM tweets t1, tweets t2
                                       WHERE t1.tid != t2.tid AND t1.tid = t2.replyto
                                        AND t1.tid = ?
                                       """, (tweetID,))
                        replies = cursor.fetchall()
                        cursor.execute("""
                                       SELECT *
                                       FROM tweets t, retweets rt
                                       WHERE t.tid = rt.tid AND t.tid = ?
                                       """, (tweetID,))
                        retweets = cursor.fetchall()
                        print("------------------------------------")
                        print("Selected tweet for information:")
                        print(f"    {tweetNum}. {row[0]} @ {row[2]} : {row[3]}")
                        print(f"\nNumber of replies: {len(replies)}")
                        print(f"Number of retweets: {len(retweets)}")
                        print("------------------------------------")
                case 'r':
                    print("----------------Reply---------------")
                    tweetNum = input("Select tweet number to reply to: ")
                    if tweetNum.isnumeric():
                        tweetNum = int(tweetNum)
                    else:
                        tweetNum = 0
                    if not (1 <= tweetNum <= index):
                        print("------------------------------------")
                        print("Invalid tweet selection.")
                        print("------------------------------------")
                    elif combinedRows[tweetNum-1][1] == 'Retweet':
                        print("------------------------------------")
                        print("You cannot reply to a retweet.")
                        print("------------------------------------")
                    else:
                        row = combinedRows[tweetNum-1]
                        replyto = row[4]
                        print("------------------------------------")
                        print("Selected tweet for reply:")
                        print(f"    {tweetNum}. {row[0]} @ {row[2]} : {row[3]}\n")
                        build_tweet(cursor, connection, user, replyto)
                case 't':
                    print("---------------Retweet--------------")
                    tweetNum = input("Select tweet number to retweet: ")
                    if tweetNum.isnumeric():
                        tweetNum = int(tweetNum)
                    else:
                        tweetNum = 0
                    if not (1 <= tweetNum <= index):
                        print("------------------------------------")
                        print("Invalid tweet selection.")
                        print("------------------------------------")
                    elif combinedRows[tweetNum-1][1] == 'Retweet':
                        print("------------------------------------")
                        print("You cannot retweet a retweet.")
                        print("------------------------------------")
                    else:
                        row = combinedRows[tweetNum-1]
                        tid = row[4]
                        usr = user[0]
                        current_datetime = datetime.now()
                        rdate = current_datetime.date()

                        cursor.execute("""
                                       SELECT *
                                       FROM retweets
                                       WHERE usr = ? AND tid = ?;
                                       """, (usr, tid))
                        exists = cursor.fetchone()
                        if exists:
                            print("------------------------------------")
                            print("You have already retweeted this tweet!")
                            print("------------------------------------")
                        else:
                            cursor.execute("""
                                           INSERT INTO retweets VALUES
                                            (?, ?, ?);
                                           """, (usr, tid, rdate))
                            connection.commit()
                            print("------------------------------------")
                            print("Your retweet to...")
                            print(f"    {tweetNum}. {row[0]} @ {row[2]} : {row[3]}")
                            print("...has been made!")
                            print("------------------------------------")
                        
            print("Options:  M - More recent activity")
            print("          I - Tweet information")
            print("          R - Reply to tweet")
            print("          T - Retweet a tweet")
            print("          C - Continue to Main Menu")
            select = get_input(['m', 'i', 'r', 't', 'c'])
    print("------------------------------------")
