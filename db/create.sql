
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
    owner INT REFERENCES Users(id),
    submit_likes BOOLEAN

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
    PRIMARY KEY (liked_by, liked, group_id),
    FOREIGN KEY (liked_by, group_id) REFERENCES MemberInGroup(user_id, group_id) ON DELETE CASCADE,
    FOREIGN KEY (liked, group_id) REFERENCES MemberInGroup(user_id, group_id) ON DELETE CASCADE
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

INSERT INTO Users (email, name, phone, gender, password)
VALUES 
    ('nl@gmail.com', 'Noah', '123-456-7890', 'M', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c'),
    ('nl1@gmail.com', 'Alice', '123-456-7891', 'F', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c'),
    ('nl2@gmail.com', 'Bob', '123-456-7892', 'M', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c'),
    ('nl3@gmail.com', 'Colby', '123-456-7893', 'M', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c'),
    ('nl4@gmail.com', 'Donald', '123-456-7894', 'M', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c'),
    ('nl5@gmail.com', 'Ezra', '123-456-7895', 'M', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c'),
    ('nl6@gmail.com', 'Sarah', '123-456-7896', 'F', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c'),
    ('nl7@gmail.com', 'Rachel', '123-456-7897', 'F', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c');

INSERT INTO Groups (name, description, password, owner, submit_likes)
VALUES
    ('Group A', 'This is Group A.', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c', 1, TRUE), -- Owned by Noah
    ('Group B', 'This is Group B.', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c', 1, FALSE), -- Owned by Noah
    ('Group C', 'This is Group C.', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c', 2, TRUE), -- Owned by Alice
    ('Group D', 'This is Group D.', 'pbkdf2:sha256:600000$6QVzyetSuLPEmbiS$b5b5f95f000927703305cbb314f753626795b8eb896b4469bb27c4382adf1f9c', 3, FALSE); -- Owned by Bob

-- Noah (id=1), Alice (id=2), Bob (id=3), Colby (id=4), Donald (id=5), Sarah (id=7), Rachel (id=8) are in all groups
-- Ezra (id=6) is in no groups

-- Members in Group A
INSERT INTO MemberInGroup (user_id, group_id)
VALUES
    (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (7, 1), (8, 1);

-- Members in Group B
INSERT INTO MemberInGroup (user_id, group_id)
VALUES
    (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (7, 2), (8, 2);

-- Members in Group C
INSERT INTO MemberInGroup (user_id, group_id)
VALUES
    (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (7, 3), (8, 3);

-- Members in Group D
INSERT INTO MemberInGroup (user_id, group_id)
VALUES
    (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (7, 4), (8, 4);
