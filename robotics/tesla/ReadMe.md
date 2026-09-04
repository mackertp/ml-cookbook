# Tesla APIs

Tesla has available APIs for developers that own their vehicles or energy products. You must own a Tesla vehicle 
to get started with the Fleet API examples outlined here. 

## Setup Requirements

1. Create a [Tesla Developer](https://developer.tesla.com/) account
2. Configure an app in the developer portal
2. Add your Tesla credentials to a `.env` file in your repo
3. Login or signup for [ngrok](https://ngrok.com/) to get a simple development server running, then start from your terminal:

```console
uname@os:~$ ngrok http 8080
```

4. Activate poetry environment to run jupyter-lab or the flask application:

```console
uname@os:~$ poetry env activate
uname@os:~$ cd robotics/tesla
uname@os:~$ jupyter-lab
```

5. Register your partner application with Tesla

- Ensure that you use set your allowed origin and redirect uri to the ngrok domain given to you.
- Execute the cells in the notebook to register your partner application with Tesla
- With the access token, execute this curl command to register the partner application:

```console
uname@os:~$ curl --location "$AUDIENCE/api/1/partner_accounts" \
  --ssl-no-revoke \
  --header 'Content-Type: application/json' \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --data '{
    "domain": "your-unique-ngrok-name.ngrok-free.dev"
}'
```

6. Explore available API endpoints and development ideas in the notebook or the Flask application.
