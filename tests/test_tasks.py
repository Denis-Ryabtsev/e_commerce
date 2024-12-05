import pytest

from tasks.email_msg import (
                                send_email,
                                after_reg,
                                verify_account,
                                after_verify,
                                reset_pass,
                                after_reset,
                                after_delete,
                                seller_order,
                                customer_order
                            )


def email_values():
    return f'test_email', f'test_name'


class TestEmail():

    def test_send_email(self, fake_smtp):
        
        email_body = {
            'Subject': 'test_subject',
            'From': 'from_test',
            'To': 'to_test',
            'Content': '<h1>Test Content</h1>'
        }

        send_email(email_body)

        fake_smtp.assert_called_once_with('smtp.gmail.com', 465)
        smtp_instance = fake_smtp.return_value.__enter__.return_value
        smtp_instance.login.assert_called_once()
        smtp_instance.send_message.asser_called_once()
        assert smtp_instance.send_message.call_args[0][0]['Subject'] == 'test_subject'
    
    def test_after_reg(self, fake_send):

        email, name = email_values()

        after_reg(email, name)

        fake_send.assert_called_once()
        assert fake_send.call_args[0][0]['Subject'] == f"Registration successfull"
        assert name in fake_send.call_args[0][0]['Content']

    def test_verify_account(self, fake_send):

        email, name = email_values()
        link = f"http://example-test.com"

        verify_account(email, link, name)

        fake_send.assert_called_once()
        assert fake_send.call_args[0][0]['Subject'] == f"Verify ur account"
        assert name, link in fake_send.call_args[0][0]['Content'] 
    
    def test_after_verify(self, fake_send):

        email, name = email_values()

        after_verify(email, name)

        fake_send.assert_called_once()
        assert fake_send.call_args[0][0]['Subject'] == f"Account was verified"
        assert name in fake_send.call_args[0][0]['Content']
    
    def test_reset_pass(self, fake_send):

        email, name = email_values()
        link = f"http://example.com"

        reset_pass(email, link, name)

        fake_send.assert_called_once()
        assert fake_send.call_args[0][0]['Subject'] == f"Reset pass"
        assert name, link in fake_send.call_args[0][0]['Content']
    
    def test_after_reset(self, fake_send):

        email, name = email_values()

        after_reset(email, name)

        fake_send.assert_called_once()
        assert fake_send.call_args[0][0]['Subject'] == f"Pass was reset"
        assert name in fake_send.call_args[0][0]['Content']
    
    def test_after_delete(self, fake_send):

        email, name = email_values()

        after_delete(email, name)

        fake_send.assert_called_once()
        assert fake_send.call_args[0][0]['Subject'] == f"Account was deleted"
        assert name in fake_send.call_args[0][0]['Content']
    
    def test_seller_order(self, fake_send):

        test_list = [
            (f'test1@gmail.com', f'ex1', 2),
            (f'test2@gmail.com', f'ex2', 1),
            (f'test3@gmail.com', f'ex3', 5)
        ]

        seller_order(test_list)

        assert fake_send.call_count == 3
        assert f'ex1' in fake_send.call_args_list[0][0][0]['Content']
        assert f'ex2' in fake_send.call_args_list[1][0][0]['Content']
        assert f'ex3' in fake_send.call_args_list[2][0][0]['Content']

    def test_customer_order(self, fake_send):

        test_list = [
            (f'test1@gmail.com', f'ex1', 2),
            (f'test2@gmail.com', f'ex2', 1),
            (f'test3@gmail.com', f'ex3', 5)
        ]

        customer_order(test_list, f'example@mail.com')

        fake_send.assert_called_once()
        assert f'example@mail.com' in fake_send.call_args[0][0]['To']
        assert f'ex3 (count: 5)' in fake_send.call_args[0][0]['Content']