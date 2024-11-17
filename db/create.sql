
CREATE TABLE Users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR UNIQUE,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR NOT NULL,
    gender VARCHAR(1) NOT NULL,
    CHECK (gender ='M' OR gender='F'),
    password VARCHAR NOT NULL
);


CREATE TABLE Groups (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR UNIQUE,
    description VARCHAR,
    password VARCHAR NOT NULL,
    owner INT REFERENCES Users(id)
);

CREATE TABLE MemberInGroup (
    user_id INTEGER REFERENCES Users(id),
    group_id INTEGER REFERENCES Groups(id), 
    PRIMARY KEY (user_id, group_id)
);

CREATE TABLE Likes (
    liked_by INTEGER REFERENCES Users(id),
    liked INTEGER REFERENCES Users(id),
    group_id INTEGER REFERENCES Groups(id), 
    CHECK (liked_by <> liked),
    PRIMARY KEY (liked_by, liked, group_id)
);


CREATE OR REPLACE FUNCTION check_users_in_group()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if liked_by is a member of the group
    IF NOT EXISTS (
        SELECT 1
        FROM MemberInGroup
        WHERE user_id = NEW.liked_by AND group_id = NEW.group_id
    ) THEN
        RAISE EXCEPTION 'User liked_by (%), is not a member of group_id (%)', NEW.liked_by, NEW.group_id;
    END IF;

    -- Check if liked is a member of the group
    IF NOT EXISTS (
        SELECT 1
        FROM MemberInGroup
        WHERE user_id = NEW.liked AND group_id = NEW.group_id
    ) THEN
        RAISE EXCEPTION 'User liked (%), is not a member of group_id (%)', NEW.liked, NEW.group_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_users_in_group
BEFORE INSERT OR UPDATE ON Likes
FOR EACH ROW
EXECUTE FUNCTION check_users_in_group();

