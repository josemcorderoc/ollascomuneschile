CREATE TABLE tweets_ollascomunes_raw (
    ID serial NOT NULL PRIMARY KEY,
	info json NOT NULL
);

CREATE TABLE tweets_ollascomunes_processed (
    tweet_id_str VARCHAR(50) PRIMARY KEY,
    created_at VARCHAR(50),
    text VARCHAR(500),
    user_id_str VARCHAR(50),
    user_screen_name VARCHAR(50),
    user_followers_count INTEGER,
    user_friends_count INTEGER,
    user_statuses_count INTEGER,
    datetime TIMESTAMP,
    comuna_identificada VARCHAR (50)
);