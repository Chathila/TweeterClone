from datetime import datetime
import re
import math


def print_main_menu():
    """
    Print the MainMenu for the Menu Screen.
    """
    print("------------MENU SCREEN-------------")
    print("------------------------------------")
    print("Options:  T - Search for Tweets")
    print("          U - Search for Users")
    print("          C - Compose a Tweet")
    print("          L - List Followers")
    print("          Q - Logout")

def compose(cursor,connection,user):
    print("-------Composing a New Tweet--------")
    build_tweet(cursor, connection, user)

def build_tweet(cursor,connection,user, replyto=None):
    tweet = input("Enter the message: ")
    while not tweet:
        print("The tweet message cannot be empty! Please try again.")
        tweet = input("Enter the message: ")
    hashtags = re.findall(r"#(\w+)", tweet)
    cursor.execute("""
                   SELECT MAX(tid)
                   FROM tweets;
                   """)
    tid = cursor.fetchone()
    if tid:
        tid = tid[0] + 1
    else:
        tid = 1
    #grabbing the date from the machine
    current_datetime = datetime.now()
    date = current_datetime.date()
    replyto = replyto
    #adding the new tweet to the tweets table
    cursor.execute("""
                   INSERT INTO tweets (tid, writer, tdate, text, replyto) 
                   VALUES (?, ?, ?, ?, ?);
                   """,(tid, user[0], date, tweet,replyto))
    connection.commit()

    print("------------------------------------")
    if replyto:
        print("Your reply...")
        print(f"    {user[2]} : {tweet}")
        print("...has been made!")
    else:
        print("Your tweet...")
        print(f"    {user[2]} : {tweet}")
        print("...has been made!")
    print("------------------------------------")

    if len(hashtags) != 0 :
        for hashtag in hashtags:
            #adding to hashtags
            cursor.execute("SELECT * FROM hashtags WHERE term = ?", (hashtag,))
            result_term = cursor.fetchone()

            if result_term is None:
                cursor.execute("INSERT INTO hashtags (term) VALUES (?)", (hashtag,))
                connection.commit()

            #adding to mentions
            cursor.execute("SELECT * FROM mentions WHERE term = ? AND tid = ? ", (hashtag,tid))
            result_mentions = cursor.fetchone()

            if result_mentions is None:
                cursor.execute("INSERT INTO mentions (tid, term) VALUES (?, ?)", (tid, hashtag))
                connection.commit()

def follow_user(follower_id, connection, cursor, user):

    if (user[0]==follower_id):
        print("You cannot follow yourself!")
        return
    # Check if already following
    cursor.execute("""
        SELECT * FROM follows WHERE flwer = ? AND flwee = ?;
    """, (user[0], follower_id))

    if cursor.fetchone():
        print("You are already following this user.")
    else:
        today = datetime.now().date()
        cursor.execute("""
            INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, ?);
        """, (user[0], follower_id, today))
        connection.commit()
        print("You are now following this user.")

def see_more_tweets(follower_id, connection, cursor):
    cursor.execute("""
        SELECT name FROM users
        WHERE usr = ?
    """, (follower_id,))

    follower_name = cursor.fetchone()
    print("------------------------------------")
    print("Showing all tweets from " + follower_name[0] +":\n")

    cursor.execute("""
        SELECT text FROM tweets
        WHERE writer = ?
        ORDER BY tdate DESC
    """, (follower_id,))

    tweets = cursor.fetchall()
    if len(tweets)==0:
        print("*There are no tweets from " + follower_name[0])
    for tweet in tweets:
        print("- " + tweet[0])
    print("")

def list_followers(connection, cursor, user):

    userID = user[0]  # Logged in user's ID
    cursor.execute("""
        SELECT u.usr, u.name
        FROM users u, follows f
        WHERE f.flwee = ? AND f.flwer = u.usr;
    """, (userID,))

    followers = cursor.fetchall()

    print("----------List Followers-----------")
    print("\nYour followers:\n")
    for idx, follower in enumerate(followers):
        print(f"{idx + 1}. {follower[1]} (User ID: {follower[0]})")
    
    print("\n-----------------------------------")
    print("Options: 1. Select a user for more options")
    print("         0. Return to main menu")

    option =  ""
    while option != '0':
        option = input("\nSelect an option: ")
        if option == '1':
            print("-----------------------------------")
            selected_index = input("Enter selected user (Enter the index of the result and not the ID): ")
            try:
                selected_index = int(selected_index) - 1
                if 0 <= selected_index < len(followers):
                    userinfo_pull(followers[selected_index][0],followers[selected_index][1], cursor, connection, user)
                    print("Your followers:\n")
                    for idx, follower in enumerate(followers):
                        print(f"{idx + 1}. {follower[1]} (User ID: {follower[0]})")
                    
                    print("\n-----------------------------------")
                    print("Options: 1. Select a user for more options")
                    print("         0. Return to main menu")
                else:
                    print("Invalid index. Please try again.")
                    print("-----------------------------------")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
                print("-----------------------------------")
        elif option == '0':
            break
        else:
            print("Invalid option selected. Please try again.")
            print("-----------------------------------")
    print("-----------------------------------")

def search_tweet(cursor, connection, user, get_input):
    print("---------Search for Tweets---------")
    keywords = input("Enter one or more keywords separated by spaces: ").split()

    terms = []
    text_matches = []
    for keyword in keywords:
        if keyword[0] == '#':
            terms.append(keyword[1:])
        else:
            text_matches.append(keyword)

    term_tweets = []
    for term in terms:
        cursor.execute("""
                    select u.name, u.usr, t.tdate, t.text, t.tid
                    from tweets t, mentions m, users u
                    where t.tid = m.tid and t.writer = u.usr and m.term = ?;
                    """, (term,))
        t = cursor.fetchall()
        if t:
            term_tweets.append(t)
        connection.commit()

    match_tweets = []
    for match in text_matches:
        match = '%' + match + '%'
        cursor.execute("""
                    select u.name, u.usr, t.tdate, t.text, t.tid
                    from tweets t, users u
                    where t.writer = u.usr 
                       and t.text like ?
                    """, (match,))
        t = cursor.fetchall()
        if t:
            match_tweets.append(t)
        connection.commit()
    
    tweets = []
    for tweet in match_tweets:
        if tweet not in tweets:
            tweets.append(tweet)
    for tweet in term_tweets:
        if tweet not in tweets:
            tweets.append(tweet)

    if not tweets:
        print("-----------------------------------")
        print("No tweets have been found!")
    else:
        print("-----------------------------------")
        tweets = tweets[0]
        tweets.sort(key=lambda a:a[2], reverse=True)
        index = 0
        stop = 5
        numRows = len(tweets)

        print("Matching tweets:\n")
        while index < numRows and index < stop:
            row = tweets[index]
            userID = row[1]
            userID = "(ID:" + str(userID) + ")"
            # print(f"{index+1}. {userID} {row[0]} @ {row[2]} : {row[3]}")
            print("{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format(str(index+1), userID, row[0], row[2], row[3]))
            index += 1
        print("\n-----------------------------------")   
        print("Options:  M - More matching tweets")
        print("          I - Tweet information")
        print("          R - Reply to tweet")
        print("          T - Retweet a tweet")
        print("          B - Back to Main Menu")
        select = get_input(['m', 'i', 'r', 't', 'b'])
        while select != 'b':
            match select:
                case 'm':
                    print("-----------------------------------")
                    stop += 5
                    if index >= numRows:
                        print("There is no more matching tweets.")
                        print("------------------------------------")
                    else:
                        print("More matching tweets:\n")
                        while index < numRows and index < stop:
                            row = tweets[index]
                            userID = row[1]
                            userID = "(ID:" + str(userID) + ")"
                            print("{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format(str(index+1), userID, row[0], row[2], row[3]))
                            index += 1
                        print("\n------------------------------------")
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
                    else:
                        row = tweets[tweetNum-1]
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
                        print(f"Number of retweets: {len(retweets)}\n")
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
                    else:
                        row = tweets[tweetNum-1]
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
                    else:
                        row = tweets[tweetNum-1]
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
                        
            print("Options:  M - More matching tweets")
            print("          I - Tweet information")
            print("          R - Reply to tweet")
            print("          T - Retweet a tweet")
            print("          B - Back to Main Menu")
            select = get_input(['m', 'i', 'r', 't', 'b'])

    print("-----------------------------------")

# def search_for_tweets(cursor, connection, user):
#     print("---------Search for Tweets---------")
#     keywords = input("Enter one or more keywords separated by spaces: ").split()

#     displayed_tweets = []
#     tweet_offset = 0 

#     def fetch_tweets(offset):
#         nonlocal displayed_tweets
#         keyword_conditions = " OR ".join([f"tweets.text LIKE '%{word}%'" for word in keywords if not word.startswith('#')])
#         hashtag_conditions = ",".join(["?" for word in keywords if word.startswith('#')])
#         hashtags = [word[1:] for word in keywords if word.startswith('#')]

#         conditions = []
#         if keyword_conditions:
#             conditions.append(f"({keyword_conditions})")
#         if hashtag_conditions:
#             conditions.append(f"hashtags.term IN ({hashtag_conditions})")
        
#         combined_conditions = " OR ".join(conditions)

#         query = f"""
#         SELECT DISTINCT tweets.tid, tweets.writer, tweets.tdate, tweets.text FROM tweets
#         LEFT JOIN mentions ON tweets.tid = mentions.tid
#         LEFT JOIN hashtags ON mentions.term = hashtags.term
#         WHERE {combined_conditions}
#         ORDER BY tweets.tdate DESC
#         LIMIT 5 OFFSET {offset};
#         """

#         # Execute the query with the list of hashtags
#         cursor.execute(query, hashtags)
#         tweets = cursor.fetchall()
#         displayed_tweets.extend(tweets)
#         return tweets

#     def display_tweets(tweets, starting_number):
#         for index, tweet in enumerate(tweets, start=starting_number):
#             print(f"{index}. [{tweet[2]}] {tweet[3]} (Tweet ID: {tweet[0]})")

#     def show_tweet_details(tweet_id):
#         cursor.execute("SELECT COUNT(*) FROM retweets WHERE tid = ?", (tweet_id,))
#         retweet_count = cursor.fetchone()[0]
#         cursor.execute("SELECT COUNT(*) FROM tweets WHERE replyto = ?", (tweet_id,))
#         reply_count = cursor.fetchone()[0]
#         print(f"Retweets: {retweet_count}, Replies: {reply_count}")

#     # Initial fetch
#     tweets = fetch_tweets(0)
#     display_tweets(tweets, starting_number=1)

#     while True:
#         print("Enter 'n' for next page, 'b' to go back, or a number to see tweet details.")

#         user_input = input().lower()

#         if user_input == 'n':
#             tweet_offset += len(tweets)
#             tweets = fetch_tweets(tweet_offset)
#             if tweets:
#                 display_tweets(tweets, starting_number=tweet_offset + 1)
#             else:
#                 print("No more tweets found.")
#                 break
#         elif user_input == 'b':
#             break
#         elif user_input.isdigit():
#             tweet_index = int(user_input) - 1
#             if tweet_offset <= tweet_index < tweet_offset + len(displayed_tweets):
#                 tweet_id = displayed_tweets[tweet_index - tweet_offset][0]
#                 show_tweet_details(tweet_id)
#             else:
#                 print("Invalid selection.")
#         else:
#             print("Invalid input.")

def search_user(cursor,connection,user):
    results = dict()
    index = 0
    print("----------Search for Users----------")

    keyword = input("Enter a keyword to search for a user: ")
    keyword = '%'+ keyword + '%'

    print("")
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE city LIKE ?
    """, (keyword,))
    total_count_city = cursor.fetchone()[0]
    maxpage_city = math.ceil(total_count_city/5)

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE name LIKE ?
    """, (keyword,))
    total_count_name = cursor.fetchone()[0]
    maxpage_name = math.ceil(total_count_name/5)

    current_name_page = 1
    current_city_page = 1

    while(True):
        results_onpage = 0
        print ("---Name Based Search---")
        if maxpage_name == 0:
            print("No Results")
        elif(current_name_page>0 and current_name_page<= maxpage_name):
            name_search = search_user_name(keyword,cursor,current_name_page)
            for name in name_search:
                index = index + 1
                results[index] = name
                str_index = str(index)
                print(str_index + "- " +"(ID:"+ str(name[0])+") " +name[1])
                results_onpage= results_onpage+1
        else:
             print ("You've reached the end of the Name-based results")

        print ("\n---City Based Search---")
        if maxpage_city == 0:
            print("No Results\n")
        

        elif(current_city_page > 0 and current_city_page <= maxpage_city):
            city_search = search_user_city(keyword,cursor,current_city_page)
            for name in city_search:
                index = index + 1
                results[index] = name
                str_index = str(index)
                print(str_index + "- " +"(ID:"+ str(name[0])+") " +name[1])
                results_onpage=results_onpage+1
        else:
            print ("You've reached the end of the City-based results")
        print("------------------------------------")

        print("Options:  1. Select a user for more options")
        print("          2. See more results")
        print("          0. Return to main menu\n")

        while(True):
            try:
                option = int((input("Select an option: ")).strip())
                if option == 1:
                    try:
                        print("------------------------------------")
                        search_index = int(input("Enter Selected user (Enter the index of result and not the ID): "))
                        if (search_index in results):
                            userinfo_pull((results[search_index][0]),(results[search_index][1]),cursor,connection,user)
                            index = index - results_onpage
                            break
                        else:
                            print("Invalid User Index entered!")
                            print("------------------------------------\n")
                    except ValueError:
                        print("Invalid User Index entered!")
                        print("------------------------------------\n")
                    index = index - results_onpage
                    #break
                elif option == 2:
                    current_city_page = current_city_page + 1
                    current_name_page = current_name_page + 1
                    print("------------------------------------\n")
                    break
                elif option == 0:
                    print("------------------------------------")
                    return
                else:
                    print("Invalid selection. Please try again\n")
            except ValueError:
                print("Invalid input. Please enter a numeric value corresponding to an option.\n")

def search_user_name(keyword, cursor,page_number):
    page_size = 5
    offset = (page_number - 1) * page_size
    cursor.execute("""
        SELECT usr,name
        FROM users
        WHERE name LIKE ?
        ORDER BY LENGTH(name), name
        LIMIT ? OFFSET ?
    """, (keyword, page_size, offset))
    usernames = cursor.fetchall()
    name_list = []
    for name in usernames:
        name_list.append((name[0],name[1]))
    return name_list

def search_user_city(keyword, cursor,page_number):
    page_size = 5
    offset = (page_number - 1) * page_size
    cursor.execute("""
        SELECT usr, name
        FROM users
        WHERE city LIKE ?
        ORDER BY LENGTH(city), city
        LIMIT ? OFFSET ?
    """, (keyword, page_size, offset))
    usernames = cursor.fetchall()
    name_list_city = []
    for name in usernames:
        name_list_city.append((name[0],name[1]))
    return name_list_city

def userinfo_pull(selected_usr,name,cursor,connection,userlogged):
    cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer = ?", (selected_usr,))
    tweet_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (selected_usr,))
    following_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (selected_usr,))
    followers_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT text FROM tweets
        WHERE writer = ?
        ORDER BY tdate DESC
        LIMIT 3;
    """, (selected_usr,))
    recent_tweets = cursor.fetchall()

    print("------------------------------------")
    print(f"\n{name} (User ID: {selected_usr})")
    print(f"Tweets: {tweet_count}, Following: {following_count}, Followers: {followers_count}")
    print("\nRecent Tweets:")

    if len(recent_tweets)==0:
        print("\n*No recent tweets from " + name)
    else:
        for tweet in recent_tweets:
            print(f" - {tweet[0]}")
    print("\n------------------------------------")


    while (True):
        print("Options:  1. Follow this user")
        print("          2. See more tweets")
        print("          0. Return to previous menu\n")
        option = int(input("Select an option: "))
        if option == 1:
            print("------------------------------------")
            follow_user(selected_usr, connection, cursor, userlogged)
            print("------------------------------------\n")
           # break
        elif option == 2:
            see_more_tweets(selected_usr, connection, cursor)
            print("------------------------------------")
            #break
        elif option == 0:
            print("------------------------------------\n")
            break
        else:
                print("Invalid selection. Please try again.")



