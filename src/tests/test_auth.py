prefix = f"api/v1/auth"


def test_create_user(fake_session, fake_user_service, test_client):
    response = test_client.post(
        url=f"{prefix}",
        json={
            "firstname": "Mike",
            "lastname": "Mean",
            "username": "MWinato09",
            "email": "andxh106@gmail.com",
            "password": "StrongPass129!",
        },
    )
    # assert
