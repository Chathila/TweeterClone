import unittest
from unittest.mock import patch, MagicMock
import io
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from login import signup_user, login_user, logout_user, get_input, print_login_menu, post_login

class TestLogin(unittest.TestCase):
    def setUp(self):
        # Mock the database connection and cursor
        self.connection = MagicMock()
        self.cursor = MagicMock()
        self.connection.cursor.return_value = self.cursor
        self.user = (1, "TestUser")

    @patch('builtins.input', side_effect=['Test User', 'test@example.com', 'Test City', 'UTC'])
    @patch('getpass.getpass', side_effect=['password123', 'password123'])
    def test_first_user_signup(self, mock_getpass, mock_input):
        # Mock database responses
        self.cursor.fetchone.return_value = None  # Simulate no existing users
        with patch('builtins.print') as mock_print:
            signup_user(self.connection, self.cursor)
            self.connection.commit.assert_called_once()
            mock_print.assert_any_call("Thank you for signing up, Test User! Your userID is 1.")

    @patch('builtins.input', side_effect=['Test User', 'test@example.com', 'Test City', 'UTC'])
    @patch('getpass.getpass', side_effect=['password123', 'password123'])
    def test_signup_with_existing_users(self, mock_getpass, mock_input):
        # Simulate existing users
        self.cursor.fetchone.return_value = (5,)  # Simulate an existing max user ID
        with patch('builtins.print') as mock_print:
            signup_user(self.connection, self.cursor)
            self.connection.commit.assert_called_once()
            mock_print.assert_any_call("Thank you for signing up, Test User! Your userID is 6.")

    @patch('builtins.input', side_effect=['Test User', 'test@example.com', 'Test City', 'UTC'])
    @patch('getpass.getpass', side_effect=['password123', 'password456'])
    def test_password_mismatch(self, mock_getpass, mock_input):
        # Mock print output
        with patch('builtins.print') as mock_print:
            signup_user(self.connection, self.cursor)

            mock_print.assert_any_call("------------------------------------")
            mock_print.assert_any_call("Error: passwords do not match. Please try again.")
            mock_print.assert_any_call("------------------------------------")

    @patch('builtins.input', side_effect=['Test User', 'test@example.com', 'Test City', 'UTC'])
    @patch('getpass.getpass', side_effect=['password123', 'password123'])
    def test_successful_signup(self, mock_getpass, mock_input):
        self.cursor.fetchone.return_value = (10,)

        # Mock print output
        with patch('builtins.print') as mock_print:
            signup_user(self.connection, self.cursor)
            mock_print.assert_any_call("------------------------------------")
            mock_print.assert_any_call("Thank you for signing up, Test User! Your userID is 11.")
            mock_print.assert_any_call("------------------------------------")

    @patch('builtins.input', side_effect=['123'])
    @patch('getpass.getpass', side_effect=['password123'])
    def test_successful_login(self, mock_getpass, mock_input):
        self.cursor.fetchone.return_value = (123, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC')

        with patch('builtins.print') as mock_print:
            logged_in, user = login_user(self.cursor)
            self.assertTrue(logged_in)
            self.assertEqual(user[2], 'Test User')
            mock_print.assert_any_call("------------------------------------")
            mock_print.assert_any_call("Login successful, welcome Test User!")
            mock_print.assert_any_call("------------------------------------")

    @patch('builtins.input', side_effect=['123'])
    @patch('getpass.getpass', side_effect=['wrongpassword'])
    def test_failed_login(self, mock_getpass, mock_input):
        self.cursor.fetchone.return_value = None
        with patch('builtins.print') as mock_print:
            logged_in, user = login_user(self.cursor)
            self.assertFalse(logged_in)
            self.assertIsNone(user)
            mock_print.assert_any_call("------------------------------------")
            mock_print.assert_any_call("Login failed! Please recheck your credentials and try again.")
            mock_print.assert_any_call("------------------------------------")

    def test_logout_successful(self):
        user = (123, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC')
        with patch('builtins.print') as mock_print:
            logged_in, user = logout_user(user)
            self.assertFalse(logged_in)
            self.assertIsNone(user)
            mock_print.assert_any_call("------------------------------------")
            mock_print.assert_any_call("Logout successful, goodbye Test User!")
            mock_print.assert_any_call("------------------------------------")

    def test_valid_input(self):
        with patch('builtins.input', side_effect=['a']):
            result = get_input(['a', 'b', 'q'])
            self.assertEqual(result, 'a')

    def test_invalid_then_valid_input(self):
        with patch('builtins.input', side_effect=['x', 'b']), patch('sys.stdout') as mock_stdout:
            result = get_input(['a', 'b', 'q'])
            self.assertEqual(result, 'b')
            printed_output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
            self.assertIn('Invalid input. Please try again.', printed_output)

    def test_case_insensitivity(self):
        with patch('builtins.input', side_effect=['A']):
            result = get_input(['a', 'b', 'q'])
            self.assertEqual(result, 'a')

    def test_empty_input(self):
        with patch('builtins.input', side_effect=['', 'b']):
            result = get_input(['a', 'b', 'q'])
            self.assertEqual(result, 'b')

    def test_print_login_menu(self):
        # Capture the output of the print_login_menu function
        expected_output = (
            "------------LOGIN SCREEN------------\n"
            "------------------------------------\n"
            "Options:  A - Signup\n"
            "          B - Login\n"
            "          Q - Quit Program\n"
        )
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            print_login_menu()
            self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['m', 'c'])
    def test_show_more_recent_activity(self, mock_input, mock_print):
        
        self.cursor.fetchall.side_effect = [
            [  
                ("User1", "Tweet", "2024-12-05", "Tweet text 1", 101, 2),
                ("User2", "Retweet", "2024-12-04", "Retweet text 2", 102, 3, "User1", 2),
                ("User3", "Tweet", "2024-12-03", "Tweet text 3", 103, 4),
                ("User4", "Retweet", "2024-12-02", "Retweet text 4", 104, 5, "User2", 3),
                ("User5", "Tweet", "2024-12-01", "Tweet text 5", 105, 6),
                ("User6", "Retweet", "2024-11-30", "Retweet text 6", 106, 7, "User3", 4),
                ("User7", "Tweet", "2024-11-29", "Tweet text 7", 107, 8)
            ],
            []
        ]

        post_login(self.connection, self.cursor, self.user)

        mock_print.assert_any_call("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format("1-Tweet", "(ID:2) User1", "2024-12-05", "Tweet text 1"))
        mock_print.assert_any_call("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format("2-Retweet", "(ID:3) User2", "2024-12-04", "(From User1@ID:2) Retweet text 2"))
        mock_print.assert_any_call("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format("3-Tweet", "(ID:4) User3", "2024-12-03", "Tweet text 3"))
        mock_print.assert_any_call("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format("4-Retweet", "(ID:5) User4", "2024-12-02", "(From User2@ID:3) Retweet text 4"))
        mock_print.assert_any_call("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format("5-Tweet", "(ID:6) User5", "2024-12-01", "Tweet text 5"))
        

        mock_print.assert_any_call("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format("6-Retweet", "(ID:7) User6", "2024-11-30", "(From User3@ID:4) Retweet text 6"))
        mock_print.assert_any_call("{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format("7-Tweet", "(ID:8) User7", "2024-11-29", "Tweet text 7"))

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['c'])
    def test_no_activity(self, mock_input, mock_print):
        self.cursor.fetchall.side_effect = [[], []]
        post_login(self.connection, self.cursor, self.user)
        mock_print.assert_any_call("You have no recent activity.")

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['c'])
    def test_only_tweets(self, mock_input, mock_print):
        self.cursor.fetchall.side_effect = [[
            ("User1", "Tweet", "2024-12-01", "Tweet text", 101, 2)
        ], []]
        post_login(self.connection, self.cursor, self.user)
        expected_output = "{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(
            "1-Tweet", "(ID:2) User1", "2024-12-01", "Tweet text"
        )
        mock_print.assert_any_call(expected_output)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['c'])
    def test_only_retweets(self, mock_input, mock_print):
        self.cursor.fetchall.side_effect = [[], [
            ("User2", "Retweet", "2024-12-01", "Retweet text", 201, 3, "User1", 2)
        ]]
        post_login(self.connection, self.cursor, self.user)
        expected_output = "{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(
            "1-Retweet", "(ID:3) User2", "2024-12-01", "(From User1@ID:2) Retweet text"
        )
        mock_print.assert_any_call(expected_output)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['m', 'c'])
    def test_pagination(self, mock_input, mock_print):
        # Simulate multiple tweets
        self.cursor.fetchall.side_effect = [[
            ("User1", "Tweet", "2024-12-01", "Tweet text 1", 101, 2),
            ("User2", "Tweet", "2024-11-30", "Tweet text 2", 102, 3)
        ], []]
        post_login(self.connection, self.cursor, self.user)

        expected_output_1 = "{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(
            "1-Tweet", "(ID:2) User1", "2024-12-01", "Tweet text 1"
        )

        expected_output_2 = "{0:<10} | {1:<25} @ {2:^12} : {3:<50}".format(
            "2-Tweet", "(ID:3) User2", "2024-11-30", "Tweet text 2"
        )

        mock_print.assert_any_call("-----------Recent Activity----------")
        mock_print.assert_any_call(expected_output_1)
        mock_print.assert_any_call(expected_output_2)

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['i', '1', 'c'])
    def test_tweet_information(self, mock_input, mock_print):
        # Arrange
        self.cursor.fetchall.side_effect = [
            [ 
                ("User1", "Tweet", "2024-12-01", "Tweet text 1", 101, 2)
            ],
            [  
                
            ],
            [   
                (101, "20", "2023-11-07", "this project is so long #tiring #DBMS", None, 44, 24, "2024-12-08", "this is a reply after a year", 101)
            ],
            [   
                (101, "20", "2023-11-07", "this project is so long #tiring #DBMS", None, 24, 101, "2024-12-08")
            ]
        ]

        
        post_login(self.connection, self.cursor, self.user)

       
        mock_print.assert_any_call("\nNumber of replies: 1")
        mock_print.assert_any_call("Number of retweets: 1")

        mock_print.assert_any_call("-----------Recent Activity----------")
        mock_print.assert_any_call("{0:^10} | {1:^25} | {2:^12} | {3:<50}".format( "#-Type", "Followee", "Date", "Text"))
        mock_print.assert_any_call("-------------------------------------------------------------------------")
        mock_print.assert_any_call("------------------------------------")
        mock_print.assert_any_call("Options:  M - More recent activity")
        mock_print.assert_any_call("          I - Tweet information")
        mock_print.assert_any_call("          R - Reply to tweet")
        mock_print.assert_any_call("          T - Retweet a tweet")
        mock_print.assert_any_call("          C - Continue to Main Menu")
        mock_print.assert_any_call("------------------------------------")

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['r', '1', 'hello', 'c'])
    def test_reply_to_tweet(self, mock_input, mock_print):
        # Arrange
        self.cursor.fetchall.side_effect = [[
            ("User1", "Tweet", "2024-12-01", "Tweet text", 101, 2)
        ], []]
        
        with patch('login.build_tweet') as mock_build_tweet:

            post_login(self.connection, self.cursor, self.user)
            mock_build_tweet.assert_called_once_with(self.cursor, self.connection, self.user, 101)
            mock_print.assert_any_call("CHATHILAAAAAA")
            mock_print.assert_any_call(f"    {1}. User1 @ 2024-12-01 : Tweet text\n")

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['t','1', 'c'])
    def test_retweet_success(self, mock_input, mock_print):
        # Arrange
        self.cursor.fetchall.side_effect = [[
            ("User1", "Tweet", "2024-12-01", "Tweet text", 101, 2)
        ], []]
        self.cursor.fetchone.return_value = None
        post_login(self.connection, self.cursor, self.user)

        mock_print.assert_any_call("------------------------------------")
        mock_print.assert_any_call("Your retweet to...")
        mock_print.assert_any_call("    1. User1 @ 2024-12-01 : Tweet text")
        mock_print.assert_any_call("...has been made!")
        mock_print.assert_any_call("------------------------------------")

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['t', '1', 'c'])
    def test_retweet_a_retweet(self, mock_input, mock_print):
        self.cursor.fetchall.side_effect = [
            [],
            [
                ("User2", "Retweet", "2024-12-01", "Retweet text", 201, 3, "User1", 2)
            ],
        ]
        
        # Act
        post_login(self.connection, self.cursor, self.user)

        # Assert
        mock_print.assert_any_call("------------------------------------")
        mock_print.assert_any_call("You cannot retweet a retweet.")
        mock_print.assert_any_call("------------------------------------")

if __name__ == '__main__':
    unittest.main(verbosity=2)