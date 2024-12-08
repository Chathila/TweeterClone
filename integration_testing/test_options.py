import unittest
from unittest.mock import MagicMock, patch
import options


class TestOptions(unittest.TestCase):
    def setUp(self):
        # Mock database connection and cursor
        self.connection = MagicMock()
        self.cursor = MagicMock()
        self.user = (1, "test_user", "Test User")  # Mock logged-in user
        self.get_input = lambda choices: choices[0]  # Mock user input as first valid choice

    def test_print_main_menu(self):
        """Test main menu prints correctly."""
        with patch("builtins.print") as mock_print:
            options.print_main_menu()
            mock_print.assert_any_call("------------MENU SCREEN-------------")
            mock_print.assert_any_call("------------------------------------")
            mock_print.assert_any_call("Options:  T - Search for Tweets")
            mock_print.assert_any_call("          U - Search for Users")
            mock_print.assert_any_call("          C - Compose a Tweet")
            mock_print.assert_any_call("          L - List Followers")
            mock_print.assert_any_call("          Q - Logout")

    def test_compose_empty_tweet(self):
        """Test compose with an empty tweet."""
        with patch("builtins.input", side_effect=[""] + ["Valid tweet"]):
            with patch("builtins.print") as mock_print:
                options.compose(self.cursor, self.connection, self.user)
                mock_print.assert_any_call("The tweet message cannot be empty! Please try again.")

    def test_compose_valid_tweet(self):
        """Test compose with a valid tweet."""
        with patch("builtins.input", side_effect=["Hello World!"]):
            with patch("builtins.print") as mock_print:
                options.compose(self.cursor, self.connection, self.user)
                self.cursor.execute.assert_called()
                mock_print.assert_any_call("Your tweet...")
                mock_print.assert_any_call(f"    Test User : Hello World!")
                mock_print.assert_any_call("...has been made!")

    def test_build_tweet_with_hashtag(self):
        """Test building a tweet with a hashtag."""
        self.cursor.fetchone.side_effect = [None, None, None]
        with patch("builtins.input", side_effect=["#hashtag tweet"]):
            options.build_tweet(self.cursor, self.connection, self.user)
            self.cursor.execute.assert_any_call("INSERT INTO hashtags (term) VALUES (?)", ("hashtag",))

    def test_follow_self(self):
        """Test trying to follow oneself."""
        with patch("builtins.print") as mock_print:
            options.follow_user(1, self.connection, self.cursor, self.user)
            mock_print.assert_any_call("You cannot follow yourself!")

    def test_follow_existing_user(self):
        """Test following an existing user."""
        self.cursor.fetchone.return_value = None
        with patch("builtins.print") as mock_print:
            options.follow_user(2, self.connection, self.cursor, self.user)
            mock_print.assert_any_call("You are now following this user.")

    def test_list_followers_with_data(self):
        """Test listing followers with multiple followers."""
        self.cursor.fetchall.return_value = [(2, "Follower1"), (3, "Follower2")]
        with patch("builtins.input", side_effect=["0"]):
            with patch("builtins.print") as mock_print:
                options.list_followers(self.connection, self.cursor, self.user)
                mock_print.assert_any_call("1. Follower1 (User ID: 2)")
                mock_print.assert_any_call("2. Follower2 (User ID: 3)")

    def test_list_followers_select_user(self):
        """Test listing followers and selecting a user for more options."""
        self.cursor.fetchall.return_value = [(2, "Follower1"), (3, "Follower2")]
        with patch("builtins.input", side_effect=["1", "1", "0"]):  # Select follower 1, then exit
            with patch("builtins.print") as mock_print:
                with patch("options.userinfo_pull") as mock_userinfo_pull:
                    options.list_followers(self.connection, self.cursor, (1, "current_user", "Current User"))
                    mock_print.assert_any_call("1. Follower1 (User ID: 2)")
                    mock_print.assert_any_call("2. Follower2 (User ID: 3)")
                    mock_userinfo_pull.assert_called_once_with(2, "Follower1", self.cursor, self.connection,
                                                               (1, "current_user", "Current User"))

    def test_list_followers_invalid_option_selection(self):
        """Test listing followers and make and invalid option selection."""
        self.cursor.fetchall.return_value = [(2, "Follower1"), (3, "Follower2")]
        with patch("builtins.input", side_effect=["2", "0",]):  # Make invalid selection (2), then exit
            with patch("builtins.print") as mock_print:
                with patch("options.userinfo_pull") as mock_userinfo_pull:
                    options.list_followers(self.connection, self.cursor, (1, "current_user", "Current User"))
                    mock_print.assert_any_call("1. Follower1 (User ID: 2)")
                    mock_print.assert_any_call("2. Follower2 (User ID: 3)")
                    mock_print.assert_any_call("Invalid option selected. Please try again.")

    def test_list_followers_invalid_user_selection(self):
        """Test listing followers and make an invalid user selection."""
        self.cursor.fetchall.return_value = [(2, "Follower1"), (3, "Follower2")]
        with patch("builtins.input", side_effect=["1", "0", "0"]):  # Make invalid selection (0)
            with patch("builtins.print") as mock_print:
                    options.list_followers(self.connection, self.cursor, (1, "current_user", "Current User"))
                    mock_print.assert_any_call("1. Follower1 (User ID: 2)")
                    mock_print.assert_any_call("2. Follower2 (User ID: 3)")
                    mock_print.assert_any_call("Invalid index. Please try again.")

    def test_search_tweet_more_tweets(self):
        """Test viewing more matching tweets."""
        self.cursor.fetchall.side_effect = [
            [("User1", 2, "2024-01-02", "First Tweet", 101), ("User2", 3, "2024-01-02", "Second Tweet", 102),
             ("User3", 4, "2024-01-02", "Third Tweet", 103), ("User4", 5, "2024-01-02", "Fourth Tweet", 104),
             ("User5", 6, "2024-01-02", "Fifth Tweet", 105), ("User6", 7, "2024-01-02", "Sixth Tweet", 106)],
        ]

        with patch("builtins.input", side_effect=["test", "m", "b"]):  # Search term, view more tweets, exit
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, lambda _: input())
                mock_print.assert_any_call(
                    "{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format("1", "(ID:2)", "User1", "2024-01-02",
                                                                        "First Tweet"))
                mock_print.assert_any_call(
                    "{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format("2", "(ID:3)", "User2", "2024-01-02",
                                                                        "Second Tweet"))
                mock_print.assert_any_call(
                    "{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format("3", "(ID:4)", "User3", "2024-01-02",
                                                                        "Third Tweet"))
                mock_print.assert_any_call(
                    "{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format("4", "(ID:5)", "User4", "2024-01-02",
                                                                        "Fourth Tweet"))
                mock_print.assert_any_call(
                    "{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format("5", "(ID:6)", "User5", "2024-01-02",
                                                                        "Fifth Tweet"))
                mock_print.assert_any_call(
                    "{0:<3}. {1:<7} {2:<20} @ {3:^12} : {4:<50}".format("6", "(ID:7)", "User6", "2024-01-02",
                                                                        "Sixth Tweet"))

    def test_search_tweet_no_more_tweets(self):
        """Test attempting to view more tweets when none exist."""
        self.cursor.fetchall.side_effect = [
            [("User1", 2, "2024-01-01", "First Tweet", 101)],
            [],
        ]

        with patch("builtins.input", side_effect=["test", "m", "b"]):  # Search term, view more tweets, exit
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, lambda _: input())
                mock_print.assert_any_call("There is no more matching tweets.")

    def test_view_tweet_info_valid(self):
        """Test viewing information for a valid tweet."""
        self.cursor.fetchall.side_effect = [[("User1", 2, "2024-01-01", "First Tweet", 101)], [], [("User2",)]]

        with patch("builtins.input", side_effect=["test", "i", "1", "b"]):  # Search term, view tweet info, exit
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, lambda _: input())
                mock_print.assert_any_call("----------Tweet Information---------")
                mock_print.assert_any_call("Selected tweet for information:")
                mock_print.assert_any_call("    1. User1 @ 2024-01-01 : First Tweet")
                mock_print.assert_any_call("\nNumber of replies: 0")
                mock_print.assert_any_call("Number of retweets: 1\n")

    def test_view_tweet_info_invalid_selection(self):
        """Test handling invalid tweet selection when viewing information."""
        self.cursor.fetchall.return_value = [("User1", 2, "2024-01-01", "First Tweet", 101)]

        with patch("builtins.input", side_effect=["test", "i", "5", "b"]):  # Invalid selection, exit
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, lambda _: input())
                mock_print.assert_any_call("Invalid tweet selection.")

    def test_reply_to_tweet_valid(self):
        """Test replying to a valid tweet."""
        self.cursor.fetchall.return_value = [("User1", 2, "2024-01-01", "First Tweet", 101)]

        with patch("builtins.input", side_effect=["test", "r", "1", "Reply message", "b"]):  # Reply to tweet
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, lambda _: input())
                mock_print.assert_any_call("----------------Reply---------------")
                mock_print.assert_any_call("Selected tweet for reply:")
                mock_print.assert_any_call("Your reply...")
                mock_print.assert_any_call("    Test User : Reply message")
                mock_print.assert_any_call("...has been made!")
                mock_print.assert_any_call("    1. User1 @ 2024-01-01 : First Tweet\n")
                self.cursor.execute.assert_called()

    def test_reply_to_tweet_invalid_selection(self):
        """Test replying to a tweet with an invalid selection."""
        self.cursor.fetchall.return_value = [("User1", 2, "2024-01-01", "First Tweet", 101)]

        with patch("builtins.input", side_effect=["test", "r", "5", "b"]):  # Invalid reply selection
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, lambda _: input())
                mock_print.assert_any_call("Invalid tweet selection.")

    def test_retweet_valid(self):
        """Test retweeting a valid tweet."""
        self.cursor.fetchall.return_value = [("User1", 2, "2024-01-01", "First Tweet", 101)]
        self.cursor.fetchone.return_value = None

        with patch("builtins.input", side_effect=["test", "t", "1", "b"]):  # Retweet and exit
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, lambda _: input())
                mock_print.assert_any_call("---------------Retweet--------------")
                mock_print.assert_any_call("Your retweet to...")
                mock_print.assert_any_call("    1. User1 @ 2024-01-01 : First Tweet")
                mock_print.assert_any_call("...has been made!")
                self.cursor.execute.assert_called()

    def test_search_tweet_no_results(self):
        """Test searching for tweets with no matching results."""
        self.cursor.fetchall.return_value = []
        with patch("builtins.input", side_effect=["nonexistent"]):
            with patch("builtins.print") as mock_print:
                options.search_tweet(self.cursor, self.connection, self.user, self.get_input)
                mock_print.assert_any_call("No tweets have been found!")

    def test_see_more_tweets_no_tweets(self):
        """Test see_more_tweets for a user with no tweets."""
        self.cursor.fetchone.side_effect = [("John Doe",)]
        self.cursor.fetchall.return_value = []
        with patch("builtins.print") as mock_print:
            options.see_more_tweets(2, self.connection, self.cursor)
            mock_print.assert_any_call("Showing all tweets from John Doe:\n")
            mock_print.assert_any_call("*There are no tweets from John Doe")

    def test_see_more_tweets_with_tweets(self):
        """Test see_more_tweets for a user with multiple tweets."""
        self.cursor.fetchone.side_effect = [("Jane Smith",)]
        self.cursor.fetchall.return_value = [
            ("Tweet 3 - Most Recent",),
            ("Tweet 2",),
            ("Tweet 1 - Oldest",),
        ]
        with patch("builtins.print") as mock_print:
            options.see_more_tweets(3, self.connection, self.cursor)
            mock_print.assert_any_call("Showing all tweets from Jane Smith:\n")
            mock_print.assert_any_call("- Tweet 3 - Most Recent")
            mock_print.assert_any_call("- Tweet 2")
            mock_print.assert_any_call("- Tweet 1 - Oldest")

    def test_search_user_select_valid(self):
        """Test selecting a user from search results."""
        self.cursor.fetchall.side_effect = [[(1, "John Doe")], []]  # Name and city search results
        self.cursor.fetchone.side_effect = [(1,), (0,)]  # Total counts for name and city searches

        with patch("builtins.input", side_effect=["test", "1", "1", "0"]):  # Search term, select user, exit
            with patch("builtins.print") as mock_print:
                with patch("options.userinfo_pull") as mock_userinfo_pull:
                    options.search_user(self.cursor, self.connection, self.user)
                    mock_userinfo_pull.assert_called_once_with(1, "John Doe", self.cursor, self.connection, self.user)
                    mock_print.assert_any_call("1- (ID:1) John Doe")

    def test_search_user_select_invalid(self):
        """Test invalid input when selecting a user."""
        self.cursor.fetchall.side_effect = [[(1, "John Doe")], []]  # Name and city search results
        self.cursor.fetchone.side_effect = [(1,), (0,)]  # Total counts for name and city searches

        with patch("builtins.input", side_effect=["test", "abc", "1", "abc", "0"]):  # Invalid inputs, then exit
            with patch("builtins.print") as mock_print:
                options.search_user(self.cursor, self.connection, self.user)
                mock_print.assert_any_call("Invalid input. Please enter a numeric value corresponding to an option.\n")
                mock_print.assert_any_call("Invalid User Index entered!")

    def test_search_user_select_no_corresponding_user(self):
        """Test invalid input when selecting a user."""
        self.cursor.fetchall.side_effect = [[(1, "John Doe")], []]  # Name and city search results
        self.cursor.fetchone.side_effect = [(1,), (0,)]  # Total counts for name and city searches

        with patch("builtins.input", side_effect=["test", "1", "5", "0"]):  # Invalid inputs, then exit
            with patch("builtins.print") as mock_print:
                options.search_user(self.cursor, self.connection, self.user)
                mock_print.assert_any_call("Invalid User Index entered!")

    def test_search_user_no_results(self):
        """Test searching for users with no results."""
        self.cursor.fetchone.return_value = [0, 0, 0]
        with patch("builtins.input", side_effect=["nonexistent", "0"]):
            with patch("builtins.print") as mock_print:
                options.search_user(self.cursor, self.connection, self.user)
                mock_print.assert_any_call("No Results")

    def test_userinfo_pull_recent_tweets(self):
        """Test pulling user information and showing recent tweets."""
        self.cursor.fetchone.side_effect = [(10,), (5,), (3,)]
        self.cursor.fetchall.side_effect = [[("Tweet 1",), ("Tweet 2",), ("Tweet 3",)]]
        with patch("builtins.input", side_effect=["0"]):
            with patch("builtins.print") as mock_print:
                options.userinfo_pull(2, "Follower1", self.cursor, self.connection, self.user)
                mock_print.assert_any_call("\nFollower1 (User ID: 2)")
                mock_print.assert_any_call("Tweets: 10, Following: 5, Followers: 3")
                mock_print.assert_any_call("\nRecent Tweets:")
                mock_print.assert_any_call(" - Tweet 1")
                mock_print.assert_any_call(" - Tweet 2")
                mock_print.assert_any_call(" - Tweet 3")

    def test_userinfo_no_recent_tweets(self):
        """Test pulling user information when there are no recent tweets."""
        self.cursor.fetchone.side_effect = [(0,), (0,), (0,)]
        self.cursor.fetchall.side_effect = [[]]
        with patch("builtins.input", side_effect=["0"]):
            with patch("builtins.print") as mock_print:
                options.userinfo_pull(2, "Follower1", self.cursor, self.connection, self.user)
                mock_print.assert_any_call("\nFollower1 (User ID: 2)")
                mock_print.assert_any_call("Tweets: 0, Following: 0, Followers: 0")
                mock_print.assert_any_call("\n*No recent tweets from Follower1")

    def test_search_user_pagination(self):
        """Test user search with pagination."""
        # Mocking return values for fetchall() and fetchone()
        self.cursor.fetchall.side_effect = [
            [(2, "User1"), (3, "User2"), (4, "User3"), (5, "User4"), (6, "User5"), (7, "User6"), (8, "User7")],
            [(9, "User8"), (10, "User9"), (11, "User10")],
            [(100, "User100")]
        ]
        self.cursor.fetchone.side_effect = [(7,), (3,)]  # Total counts for city and name search

        # Input search term, next page, then exit
        with patch("builtins.input", side_effect=["test", "2", "0"]):
            with patch("builtins.print") as mock_print:
                options.search_user(self.cursor, self.connection, self.user)

                # Assertions for printed outputs
                mock_print.assert_any_call("1- (ID:2) User1")
                mock_print.assert_any_call("2- (ID:3) User2")
                mock_print.assert_any_call("3- (ID:4) User3")
                mock_print.assert_any_call("4- (ID:5) User4")
                mock_print.assert_any_call("5- (ID:6) User5")
                mock_print.assert_any_call("6- (ID:7) User6")
                mock_print.assert_any_call("7- (ID:8) User7")
                mock_print.assert_any_call("8- (ID:9) User8")
                mock_print.assert_any_call("9- (ID:10) User9")
                mock_print.assert_any_call("10- (ID:11) User10")
                mock_print.assert_any_call("You've reached the end of the Name-based results")