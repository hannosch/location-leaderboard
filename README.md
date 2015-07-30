# leaderboard-server

[![Build Status](https://api.travis-ci.org/JaredKerim-Mozilla/leaderboard-server.svg)](https://travis-ci.org/JaredKerim-Mozilla/leaderboard-server)

[![Coverage Status](https://coveralls.io/repos/JaredKerim-Mozilla/leaderboard-server/badge.svg?branch=master&service=github)](https://coveralls.io/github/JaredKerim-Mozilla/leaderboard-server?branch=master)

Overview
---

The leaderboard-server is a RESTful service which implements an API
for submitting data which describes the geolocation stumbling efforts
of contributions to the Mozilla Location Service project.  Mozilla Stumbler
users can submit data to the leaderboard-server about how many networks
were detected within a geospatial 'tile' at a given time, and then query
the top contributions.

# API Interface

Get Contribution Config
----
  Get the configuration parameters necessary to prepare contribution data for submission.
  All of the individual observations a stumbler has made should be grouped into blocks, the size
  and duration of which are determined by the results of this call.

* **URL**

  https://leaderboard.services.mozilla.com/api/v1/contributions/config/

* **Method:**

  `GET`

*  **URL Params**

  None

* **Data Params**

  None

* **Request Headers**

  None

* **Success Response:**

  * **Code:** 200

  JSON encoding

      {
        tile_size: <int>,
        record_duration: <int>
      }

  * **tile_size**

  The size of each side of a square tile in meters.

  * **record_duration**

  The length each contribution record in seconds.

* **Error Responses:**

  None

* **Sample Call:**

        $.ajax({
          url: "https://leaderboard.services.mozilla.com/api/v1/contributions/config/",
          dataType: "json",
          type : "GET",
          success : function(r, data) {
            console.log(data);
          }
        });

Add Stumbles
----
 Submit the number of networks detected within a series of tiles for a given contributor.

* **URL**

  https://leaderboard.services.mozilla.com/api/v1/contributions/add_stumbles/

* **Method:**

  `POST`

*  **URL Params**

  None

* **Data Params**

  The data submitted in a single POST request describes how many observations 
  were made by a contributor.  Each observation is made at a given time and place,
  however to reduce the size of the data sent, the observations are grouped into 'tiles'.
  The tile size is requested from the server, and is measured in meters.  Observations are
  then grouped into tiles of that size and summed.  Each data point sent 
  describes the coordinates of a point within that tile (the server will round the coordinates
  provided to the nearest containing tile), and the number of observations made within that
  tile.

  * **POST body (JSON encoded)**

          {
            items: [
              {
                time: <float>,
                tile_easting_m: <int>,
                tile_northing_m: <int>,
                observations: <int>
              }
            ]
          }

  * **time**

  A UNIX time stamp in seconds that represents the time when the observations for the given tile
  were made.

  * **tile_easting_m**

  The number of meters east from 0,0 in the [EPSG 3857 coordinate system](http://spatialreference.org/ref/sr-org/7483/)

  * **tile_northing_m**

  The number of meters north from 0,0 in the [EPSG 3857 coordinate system](http://spatialreference.org/ref/sr-org/7483/)

  * **observations**

  The number of observations made by the contributor since the last time they submitted
  to the leaderboard within the specified 1km x 1km tile.

* **Request Headers**

  * Content-Encoding

  The submission API optionally supports gzipped payloads.  To submit a gzipped
  request, include the gzipped JSON data in the request body and add the
  header to the request.

  Example: `Content-Encoding: gzip`

  * Authorization

  A successful submission must include a valid Firefox Accounts authorization
  bearer token

  Example: `Authorization: Bearer kf94k5jsgsl3kj`

* **Success Response:**

  * **Code:** 201

* **Error Responses:**

  * **Code:** 400 INVALID  <br />
    **Content:** `{"detail":"JSON parse error - Expecting object: line 1 column 1 (char 0)"}`

  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** `{"detail":"Unable to determine a valid Firefox Accounts authorization token"}`

* **Sample Call:**

        $.ajax({
          url: "https://leaderboard.services.mozilla.com/api/v1/add_stumbles/",
          dataType: "json",
          beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer fksdf90sek4jk50');
          },
          data : {
            items: [
              {
                time: 1234567890,
                tile_easting_m: -8872100,
                tile_northing_m: 5435700,
                observations: 100
              },
              {
                time: 1234567890,
                tile_easting_m: -8872100,
                tile_northing_m: 5435700,
                observations: 100
              },
              {
                time: 1234567890,
                tile_easting_m: -8892100,
                tile_northing_m: 5435700,
                observations: 100
              }
            ]
          },
          type : "POST",
          success : function(req) {
            console.log(req);
          }
        });

Get Leaders
----
  Get the leaders for a given Country.

* **URL**

  https://leaderboard.services.mozilla.com/api/v1/leaders/country/<country_id: int>/

* **Method:**

  `GET`

*  **URL Params**

  * country_id : `int`

  A country_id is an id which can be found by calling the [Get Countries](#get-countries) API endpoint.

* **Data Params**

  None

* **Request Headers**

  None

* **Success Response:**

  * **Code:** 200

  JSON encoding

        {
          country_name: <str>,
          leaders: [
            {
              name: <str>,
              observations: <int>
            }
          ]
        }

* **Error Responses:**

  None

* **Sample Call:**

        $.ajax({
          url: "https://leaderboard.services.mozilla.com/api/v1/leaders/country/1/",
          dataType: "json",
          data: {
            country_id: 1,
          }
          type : "GET",
          success : function(r, data) {
            console.log(data);
          }
        });
