# curiosity_monitoring

curiosity_monitoring collects waypoint data from NASA's official website of the curiosity rover.
It provides Graphql API Queries to interact with the data collected.

The packages required to execute the scripts can be installed  by executing the pip command,

`pip install -r requirements.txt`

The curiosity_waypoints.py is a simple python script which utilizes Chrome browser.
It creates a json file containing waypoints data under monitoring\curiosity\fixtures.

The script can be executed by using the command.

`python curiosity_waypoints.py`

The waypoints data fetched by the script can be loaded to the SQLite3 database.
While loading the database for the first time, the following commands are executed for creation of the tables to store the data

`python manage.py makemigrations`
`python manage.py migrate`

The latest data is loaded to the database by executing the command,

`python manage.py loaddata monitoring\curiosity\fixtures\curiosity_rover_data`

The server can be connected by executing the following command from commandline,

`python manage.py runserver`

The GraphiQL view is loaded using the url

`http://localhost:8000/graphql`

The sample GraphQL APIs queries and outputs are available under data directory.

PS: Suggestions and corrections are always welcome.