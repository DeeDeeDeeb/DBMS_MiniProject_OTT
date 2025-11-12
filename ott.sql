CREATE DATABASE ott;
USE ott;


CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name  VARCHAR(50),
    registration_date DATE NOT NULL
);


CREATE TABLE User_Email (
    email_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    email VARCHAR(100) UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);


CREATE TABLE User_Phone (
    phone_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);


CREATE TABLE Subscription_Plan (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(50) UNIQUE NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    duration_months INT CHECK (duration_months > 0)
);


CREATE TABLE User_Subscription (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    plan_id INT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('active','expired','cancelled') NOT NULL,
    auto_renewal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES Subscription_Plan(plan_id),
    UNIQUE(user_id, plan_id, start_date)  -- prevent duplicate overlapping subscriptions
);


CREATE TABLE Profile (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    profile_name VARCHAR(50) NOT NULL,
    age_restriction INT,
    is_kids_profile BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);


CREATE TABLE Content (
    content_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    release_date DATE,
    content_type ENUM('movie','series') NOT NULL,
    rating ENUM('G','PG','PG-13','R','NC-17') NOT NULL,
    language VARCHAR(50)
);


CREATE TABLE Genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);


CREATE TABLE Content_Genre (
    content_id INT,
    genre_id INT,
    PRIMARY KEY(content_id, genre_id),
    FOREIGN KEY (content_id) REFERENCES Content(content_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE
);


CREATE TABLE Season (
    season_id INT AUTO_INCREMENT PRIMARY KEY,
    content_id INT,
    season_number INT NOT NULL,
    title VARCHAR(200),
    total_episodes INT CHECK (total_episodes >= 0),
    FOREIGN KEY (content_id) REFERENCES Content(content_id) ON DELETE CASCADE
);


CREATE TABLE Episode (
    episode_id INT AUTO_INCREMENT PRIMARY KEY,
    season_id INT,
    episode_number INT NOT NULL,
    title VARCHAR(200),
    duration INT CHECK (duration > 0), -- duration in minutes
    FOREIGN KEY (season_id) REFERENCES Season(season_id) ON DELETE CASCADE
);

CREATE TABLE Watchlist (
    watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
    profile_id INT,
    content_id INT,
    added_date DATE,
    FOREIGN KEY (profile_id) REFERENCES Profile(profile_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES Content(content_id) ON DELETE CASCADE,
    UNIQUE(profile_id, content_id) -- prevent duplicate entries
);


CREATE TABLE Watch_History (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    profile_id INT,
    content_id INT,
    episode_id INT NULL,
    device_id INT,
    watch_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    completion_percentage DECIMAL(5,2) CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    FOREIGN KEY (profile_id) REFERENCES Profile(profile_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES Content(content_id) ON DELETE CASCADE,
    FOREIGN KEY (episode_id) REFERENCES Episode(episode_id) ON DELETE SET NULL
);



CREATE TABLE Rating_Review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    profile_id INT,
    content_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    FOREIGN KEY (profile_id) REFERENCES Profile(profile_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES Content(content_id) ON DELETE CASCADE,
    UNIQUE(profile_id, content_id) -- one review per profile per content
);


CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    subscription_id INT,
    amount DECIMAL(8,2) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('card','upi','netbanking','wallet') NOT NULL,
    status ENUM('success','failed','pending') NOT NULL,
    FOREIGN KEY (subscription_id) REFERENCES User_Subscription(subscription_id) ON DELETE CASCADE
);


CREATE TABLE Device (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    device_name VARCHAR(100),
    device_type ENUM('TV','Mobile','Laptop','Tablet','Other'),
    last_used DATETIME,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);



INSERT INTO User (first_name, last_name, registration_date)
VALUES
('Aisha', 'Rahal','2024-11-05' ),
('Suraj', 'Patel', '2024-02-15'),
('Aisha', 'Khan', '2024-03-05'),
('Rohit', 'Sharma', '2024-03-20'),
('Neha', 'Verma', '2024-04-10'),
('Arjun', 'Menon', '2024-05-01'),
('Sara', 'Kapoor', '2024-06-12'),
('Dev', 'Singh', '2024-07-01'),
('Priya', 'Nair', '2024-07-15'),
('Vikram', 'Rao', '2024-08-01');


SELECT * FROM user;

INSERT INTO User_Email (user_id, email) VALUES
(1, 'aisha@example.com'),
(2, 'suraj2@example.com'),
(3, 'aisha.k@example.com'),
(4, 'rohit.sharma@example.com'),
(5, 'neha.v@example.com'),
(6, 'arjun.menon@example.com'),
(7, 'sara.kapoor@example.com'),
(8, 'dev.singh@example.com'),
(9, 'priya.nair@example.com'),
(10, 'vikram.rao@example.com');

SELECT * FROM  user_Email;



INSERT INTO User_Phone (user_id, phone_number) VALUES
(1, '9876543210'),
(2, '9123456780'),
(3, '9876012345'),
(4, '9887654321'),
(5, '9700112233'),
(6, '9898989898'),
(7, '9666777888'),
(8, '9555444333'),
(9, '9990001111'),
(10, '9787878787');
SELECT * FROM  user_Phone;


SELECT * FROM  Subscription_Plan;

INSERT INTO Subscription_Plan (plan_name, price, duration_months)
VALUES 
('Basic', 199.00, 1),
('Standard', 499.00, 1),
('Premium', 799.00, 1);


INSERT INTO User_Subscription (user_id, plan_id, start_date, end_date, status, auto_renewal)
VALUES
(1, 3, '2024-03-01', '2024-03-31', 'active', TRUE),
(2, 1, '2024-03-05', '2024-04-04', 'expired', FALSE),
(3, 2, '2024-03-10', '2024-04-10', 'active', TRUE),
(4, 3, '2024-03-15', '2025-03-14', 'active', TRUE),
(5, 3, '2024-04-05', '2024-05-04', 'cancelled', FALSE),
(6, 2, '2024-05-01', '2024-05-31', 'expired', FALSE),
(7, 3, '2024-06-12', '2024-07-11', 'active', TRUE),
(8, 1, '2024-07-01', '2024-07-31', 'expired', FALSE),
(9, 3, '2024-07-15', '2025-07-14', 'active', TRUE),
(10, 2, '2024-08-01', '2024-08-31', 'active', TRUE);
SELECT * FROM  User_Subscription;

INSERT INTO Profile (user_id, profile_name, age_restriction, is_kids_profile)
VALUES
(1, 'Aisha_Main', 18, FALSE),
(1, 'Kids_Mode', 12, TRUE),
(2, 'Suraj_Main', 18, FALSE),
(3, 'Aisha_Main', 18, FALSE),
(4, 'Rohit_Main', 18, FALSE),
(5, 'Neha_Kids', 10, TRUE),
(6, 'Arjun_Main', 18, FALSE),
(7, 'Sara_Main', 18, FALSE),
(8, 'Dev_Main', 18, FALSE),
(9, 'Priya_Main', 18, FALSE),
(10, 'Vikram_Main', 18, FALSE);

SELECT * FROM  Profile;

INSERT INTO Content (title, description, release_date, content_type, rating, language)
VALUES
('Inception', 'A mind-bending sci-fi thriller.', '2010-07-16', 'movie', 'PG-13', 'English'),
('Stranger Things', 'A mystery sci-fi TV series.', '2016-07-15', 'series', 'PG-13', 'English'),
('Money Heist', 'Spanish heist drama.', '2017-05-02', 'series', 'R', 'Spanish'),
('Interstellar', 'Space exploration and love beyond time.', '2014-11-07', 'movie', 'PG-13', 'English'),
('The Dark Knight', 'Batman faces the Joker.', '2008-07-18', 'movie', 'PG-13', 'English'),
('Lucifer', 'The Devil helps LAPD solve crimes.', '2016-01-25', 'series', 'R', 'English'),
('Coco', 'Animated adventure about family and music.', '2017-11-22', 'movie', 'G', 'English'),
('Dangal', 'Wrestling-based Indian biopic.', '2016-12-21', 'movie', 'PG', 'Hindi'),
('Wednesday', 'Addams Family’s daughter in Nevermore Academy.', '2022-11-23', 'series', 'PG-13', 'English'),
('The Witcher', 'Fantasy series about monster hunting.', '2019-12-20', 'series', 'R', 'English');

SELECT * FROM  Content;

INSERT INTO Genre (genre_name, description)
VALUES
('Sci-Fi', 'Science Fiction'),
('Thriller', 'Suspense and thrill'),
('Drama', 'Emotional storytelling'),
('Action', 'Fast-paced adventure'),
('Comedy', 'Humor and light-hearted entertainment'),
('Fantasy', 'Magic and mythical elements'),
('Animated', 'Cartoon and CGI-based content'),
('Biography', 'Real-life based story'),
('Mystery', 'Puzzle and investigation plots');

SELECT * FROM  Genre;

INSERT INTO Content_Genre (content_id, genre_id) VALUES
(1,1),(1,2),
(2,1),(2,3),
(3,3),(3,2),
(4,1),(4,3),
(5,4),(5,2),
(6,3),(6,9),
(7,7),(7,3),
(8,8),(8,3),
(9,3),(9,9),
(10,6),(10,4);

select * from Content_Genre;



INSERT INTO Season (content_id, season_number, title, total_episodes)
VALUES
(2,1,'Stranger Things S1',8),
(2,2,'Stranger Things S2',9),
(3,1,'Money Heist S1',13),
(3,2,'Money Heist S2',9),
(6,1,'Lucifer S1',13),
(9,1,'Wednesday S1',8),
(10,1,'The Witcher S1',8),
(10,2,'The Witcher S2',8);

select * from Season;

INSERT INTO Episode (season_id, episode_number, title, duration)
VALUES
(1, 1, 'Chapter One: The Vanishing of Will Byers', 50),
(1, 2, 'Chapter Two: The Weirdo on Maple Street', 48),
(3,1,'Episode 1',55),
(3,2,'Episode 2',54),
(5,1,'Pilot',45),
(6,1,'Wednesday’s Child',47),
(7,1,'The End’s Beginning',61),
(8,1,'A Grain of Truth',59);
select * from Episode;


INSERT INTO Watchlist (profile_id, content_id, added_date)
VALUES
(1,1,'2024-03-02'),
(2,2,'2024-03-03'),
(3,3,'2024-03-10'),
(4,4,'2024-03-15'),
(5,7,'2024-04-10'),
(6,6,'2024-05-05'),
(7,9,'2024-06-12'),
(8,8,'2024-07-01'),
(9,10,'2024-07-15'),
(10,5,'2024-08-01');

select * from Watchlist;




INSERT INTO Watch_History (profile_id, content_id, episode_id, watch_date, completion_percentage)
VALUES
(1,1,NULL,'2024-03-05 20:15:00',100.00),
(2,2,1,'2024-03-07 21:00:00',50.00),
(3,3,3,'2024-03-08 19:45:00',90.00),
(4,4,NULL,'2024-03-20 18:30:00',100.00),
(5,7,NULL,'2024-04-12 17:00:00',100.00),
(6,6,5,'2024-05-07 21:15:00',80.00),
(7,9,6,'2024-06-14 22:00:00',70.00),
(8,8,NULL,'2024-07-03 19:30:00',100.00),
(9,10,7,'2024-07-18 20:45:00',50.00),
(10,5,NULL,'2024-08-03 18:00:00',100.00);

select * from Watch_History ;


INSERT INTO Rating_Review (profile_id, content_id, rating, review_text)
VALUES
(1,1,5,'Amazing sci-fi!'),
(1,2,4,'Very engaging series.'),
(3,3,5,'Mind-blowing heist drama.'),
(4,4,5,'Emotionally powerful.'),
(5,7,4,'Loved the visuals and music.'),
(6,6,3,'Good concept but slow.'),
(7,9,4,'Enjoyable mystery.'),
(8,8,5,'Inspiring biopic.'),
(9,10,5,'Epic fantasy!'),
(10,5,4,'Classic superhero film.');

select * from Rating_Review ;

INSERT INTO Payment (subscription_id, amount, payment_date, payment_method, status)
VALUES
(1, 199.00, '2024-03-05 12:15:00', 'upi', 'success'),
(2,499.00,'2024-03-10 09:45:00','wallet','success'),
(3,8999.00,'2024-03-15 11:00:00','card','success'),
(4,799.00,'2024-04-05 10:30:00','netbanking','failed'),
(5,499.00,'2024-05-01 08:30:00','card','success'),
(6,799.00,'2024-06-12 13:45:00','upi','success'),
(7,199.00,'2024-07-01 09:10:00','wallet','success'),
(8,8999.00,'2024-07-15 11:20:00','card','success'),
(9,8999.00,'2024-11-15 11:25:00','wallet','success'),
(10,499.00,'2024-08-01 15:00:00','upi','success');

select * from Payment ;


INSERT INTO Device (user_id, device_name, device_type, last_used)
VALUES
(1,'Aishas iPhone','Mobile','2024-03-08 18:30:00'),
(1,'Aisha Smart TV','TV','2024-03-09 20:00:00'),
(2,'Suraj Laptop','Laptop','2024-03-07 22:00:00'),
(3,'Aisha Pixel','Mobile','2024-03-10 21:00:00'),
(4,'Rohit iPad','Tablet','2024-03-20 22:30:00'),
(5,'Neha TV','TV','2024-04-12 19:00:00'),
(6,'Arjun Laptop','Laptop','2024-05-05 20:15:00'),
(7,'Sara iPhone','Mobile','2024-06-14 23:00:00'),
(8,'Dev TV','TV','2024-07-03 18:45:00'),
(9,'Priya MacBook','Laptop','2024-07-18 19:30:00'),
(10,'Vikram Smart TV','TV','2024-08-02 21:00:00');

select * from Device ;


-- Triggers

-- Trigger 1 — Auto-update subscription status
DELIMITER $$
CREATE TRIGGER update_subscription_status
BEFORE UPDATE ON User_Subscription
FOR EACH ROW
BEGIN
    IF NEW.end_date < CURDATE() THEN
        SET NEW.status = 'expired';
    END IF;
END$$
DELIMITER ;

-- Trigger 2 — Log every successful payment
CREATE TABLE Payment_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT,
    log_message VARCHAR(255),
    log_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER payment_success_log
AFTER INSERT ON Payment
FOR EACH ROW
BEGIN
    IF NEW.status = 'success' THEN
        INSERT INTO Payment_Log (payment_id, log_message)
        VALUES (NEW.payment_id, CONCAT('Payment of ₹', NEW.amount, ' by Subscription ID ', NEW.subscription_id, ' was successful.'));
    END IF;
END$$
DELIMITER ;

-- Trigger 3 — Prevent duplicate review per profile per content
DELIMITER $$
CREATE TRIGGER prevent_duplicate_review
BEFORE INSERT ON Rating_Review
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Rating_Review 
               WHERE profile_id = NEW.profile_id AND content_id = NEW.content_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Profile has already reviewed this content.';
    END IF;
END$$
DELIMITER ;
 
 
-- Trigger 4 — Update auto-renewal payments automatically
DELIMITER $$
CREATE TRIGGER auto_renew_payment
AFTER UPDATE ON User_Subscription
FOR EACH ROW
BEGIN
    IF NEW.auto_renewal = TRUE AND NEW.status = 'active' AND OLD.end_date <> NEW.end_date THEN
        INSERT INTO Payment (subscription_id, amount, payment_method, status)
        SELECT NEW.subscription_id, SP.price, 'card', 'success'
        FROM Subscription_Plan SP
        WHERE SP.plan_id = NEW.plan_id;
    END IF;
END$$
DELIMITER ;

-- Trigger 5 — Watch History Auto-Update
-- If a profile watches 100%, the system automatically adds it to the watchlist if not already there.
DELIMITER $$
CREATE TRIGGER auto_add_watchlist
AFTER INSERT ON Watch_History
FOR EACH ROW
BEGIN
    IF NEW.completion_percentage = 100 THEN
        IF NOT EXISTS (
            SELECT 1 FROM Watchlist 
            WHERE profile_id = NEW.profile_id AND content_id = NEW.content_id
        ) THEN
            INSERT INTO Watchlist (profile_id, content_id, added_date)
            VALUES (NEW.profile_id, NEW.content_id, CURDATE());
        END IF;
    END IF;
END$$
DELIMITER ;

-- Procedures 

-- Procedure 1 — Add New User with Email and Phone
DELIMITER $$
CREATE PROCEDURE AddNewUser(
    IN fname VARCHAR(50),
    IN lname VARCHAR(50),
    IN email VARCHAR(100),
    IN phone VARCHAR(15)
)
BEGIN
    DECLARE new_id INT;
    INSERT INTO User (first_name, last_name, registration_date)
    VALUES (fname, lname, CURDATE());
    
    SET new_id = LAST_INSERT_ID();
    
    INSERT INTO User_Email (user_id, email) VALUES (new_id, email);
    INSERT INTO User_Phone (user_id, phone_number) VALUES (new_id, phone);
END$$
DELIMITER ;

-- Example:
-- CALL AddNewUser('Tia', 'Ram', 'tiya.roy@example.com', '9145347834');

-- Procedure 2 — Renew Subscription
-- Extends the subscription by its plan duration and logs payment automatically.
DELIMITER $$
CREATE PROCEDURE RenewSubscription(IN sub_id INT)
BEGIN
    DECLARE months INT;
    DECLARE amount DECIMAL(8,2);
    DECLARE pid INT;
    
    SELECT SP.duration_months, SP.price, SP.plan_id 
    INTO months, amount, pid
    FROM User_Subscription US
    JOIN Subscription_Plan SP ON US.plan_id = SP.plan_id
    WHERE US.subscription_id = sub_id;
    
    UPDATE User_Subscription 
    SET end_date = DATE_ADD(end_date, INTERVAL months MONTH),
        status = 'active'
    WHERE subscription_id = sub_id;
    
    INSERT INTO Payment (subscription_id, amount, payment_method, status)
    VALUES (sub_id, amount, 'upi', 'success');
END$$
DELIMITER ;

-- Example:
-- CALL RenewSubscription(2);


-- Procedure 3 — Show User Watch History Summary
DELIMITER $$
CREATE PROCEDURE GetWatchHistory(IN profileId INT)
BEGIN
    SELECT 
        C.title,
        WH.watch_date,
        WH.completion_percentage
    FROM 
        Watch_History WH
    JOIN Content C ON WH.content_id = C.content_id
    WHERE WH.profile_id = profileId
    ORDER BY WH.watch_date DESC;
END$$
DELIMITER ;

-- Example:
-- CALL GetWatchHistory(1);


-- Procedure 4 — Get Top Rated Content
-- Returns top N contents based on average rating.
DELIMITER $$
CREATE PROCEDURE TopRatedContent(IN limitN INT)
BEGIN
    SELECT 
        C.title,
        AVG(R.rating) AS avg_rating,
        COUNT(R.review_id) AS total_reviews
    FROM Rating_Review R
    JOIN Content C ON R.content_id = C.content_id
    GROUP BY C.title
    ORDER BY avg_rating DESC
    LIMIT limitN;
END$$
DELIMITER ;

-- Example:
-- CALL TopRatedContent(5);

-- Functions
-- Function 1 — Calculate Days Left in Subscription
DELIMITER $$
CREATE FUNCTION DaysLeft(sub_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE days_left INT;
    SELECT DATEDIFF(end_date, CURDATE()) INTO days_left
    FROM User_Subscription WHERE subscription_id = sub_id;
    RETURN days_left;
END$$
DELIMITER ;

-- Example:
-- SELECT subscription_id, DaysLeft(subscription_id) AS Remaining_Days FROM User_Subscription;

-- Function 2 — Check if Subscription is Active
DELIMITER $$
CREATE FUNCTION IsActive(uid INT)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt
    FROM User_Subscription
    WHERE user_id = uid AND status = 'active';
    RETURN (cnt > 0);
END$$
DELIMITER ;

-- Example:
-- SELECT user_id, IsActive(user_id) AS active_now FROM User;

-- Function 3 — Calculate Average Rating for a Content
DELIMITER $$
CREATE FUNCTION AvgContentRating(cid INT)
RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
    DECLARE avg_rate DECIMAL(3,2);
    SELECT AVG(rating) INTO avg_rate
    FROM Rating_Review
    WHERE content_id = cid;
    RETURN avg_rate;
END$$
DELIMITER ;

-- Example:
-- SELECT title, AvgContentRating(content_id) AS avg_rating FROM Content;



CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50),
    role ENUM('Admin', 'Support', 'Viewer')
);

INSERT INTO admin (username, password, role)
VALUES 
('admin', 'admin123', 'Admin'),
('support', 'support123', 'Support'),
('viewer', 'viewer123', 'Viewer');


CREATE TABLE Device_Activity (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    profile_id INT NOT NULL,
    device_id INT NOT NULL,
    content_id INT NOT NULL,
    episode_id INT NULL,
    watch_start DATETIME DEFAULT CURRENT_TIMESTAMP,
    watch_end DATETIME NULL,
    completion_percentage DECIMAL(5,2) CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    FOREIGN KEY (profile_id) REFERENCES Profile(profile_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES Device(device_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES Content(content_id) ON DELETE CASCADE,
    FOREIGN KEY (episode_id) REFERENCES Episode(episode_id) ON DELETE SET NULL
);

DELIMITER $$
CREATE TRIGGER log_device_activity
AFTER INSERT ON Watch_History
FOR EACH ROW
BEGIN
    -- Record the watch activity tied to device used in Watch_History
    INSERT INTO Device_Activity (profile_id, device_id, content_id, episode_id, watch_start, completion_percentage)
    VALUES (NEW.profile_id, NEW.device_id, NEW.content_id, NEW.episode_id, NEW.watch_date, NEW.completion_percentage);
END$$
DELIMITER ;

INSERT INTO Device_Activity 
(profile_id, device_id, content_id, episode_id, watch_start, watch_end, completion_percentage)
VALUES
(1, 1, 3, NULL, '2025-11-03 20:00:00', '2025-11-03 21:45:00', 100.00),
(2, 2, 6, 5, '2025-11-04 18:30:00', '2025-11-04 19:15:00', 95.50),
(3, 3, 8, NULL, '2025-11-02 22:00:00', NULL, 40.00),

-- Profile 1 rewatched Episode 2 of Content 4 on Tablet
(1, 4, 4, 2, '2025-11-01 21:30:00', '2025-11-01 22:20:00', 100.00),
(4, 1, 7, NULL, '2025-11-05 17:00:00', NULL, 68.25);

SELECT 
    U.first_name AS User,
    D.device_name AS Device,
    D.device_type AS Device_Type,
    C.title AS Content_Title,
    DA.watch_start AS Watched_On,
    DA.completion_percentage AS Completion
FROM Device_Activity DA
JOIN Profile P ON DA.profile_id = P.profile_id
JOIN User U ON P.user_id = U.user_id
JOIN Device D ON DA.device_id = D.device_id
JOIN Content C ON DA.content_id = C.content_id
ORDER BY U.user_id, DA.watch_start DESC;

INSERT INTO Device_Activity 
(profile_id, device_id, content_id, episode_id, watch_start, watch_end, completion_percentage)
VALUES
-- Profile 1 watched a movie on Smart TV
(1, 1, 3, NULL, '2025-11-03 20:00:00', '2025-11-03 21:45:00', 100.00),

-- Profile 2 watched Episode 5 of Content 6 on Mobile
(2, 2, 6, 5, '2025-11-04 18:30:00', '2025-11-04 19:15:00', 95.50),

-- Profile 3 started a movie on Laptop but didn’t finish
(3, 3, 8, NULL, '2025-11-02 22:00:00', NULL, 40.00),

-- Profile 1 rewatched Episode 2 of Content 4 on Tablet
(1, 4, 4, 2, '2025-11-01 21:30:00', '2025-11-01 22:20:00', 100.00),

-- Profile 4 partially watched Content 7 on Smart TV
(4, 1, 7, NULL, '2025-11-05 17:00:00', NULL, 68.25),

-- Profile 2 binge-watched Episode 6 of Content 6 on Mobile
(2, 2, 6, 6, '2025-11-05 20:10:00', '2025-11-05 20:55:00', 92.00),

-- Profile 3 watched Content 9 on Laptop
(3, 3, 9, NULL, '2025-11-04 16:45:00', '2025-11-04 18:25:00', 100.00),

-- Profile 1 started Episode 3 of Content 4 but paused midway
(1, 4, 4, 3, '2025-11-05 19:00:00', NULL, 55.00),

-- Profile 4 finished Episode 1 of Content 10 on Smart TV
(4, 1, 10, 1, '2025-11-03 22:10:00', '2025-11-03 22:45:00', 100.00),

-- Profile 2 rewatched Content 5 on Mobile
(2, 2, 5, NULL, '2025-11-02 14:00:00', '2025-11-02 15:50:00', 100.00),

-- Profile 3 watched Content 2 on Laptop, dropped early
(3, 3, 2, NULL, '2025-11-01 13:10:00', NULL, 20.00),

-- Profile 4 watched Episode 2 of Content 10
(4, 1, 10, 2, '2025-11-04 19:30:00', '2025-11-04 20:15:00', 88.00),

-- Profile 1 watched Content 1 fully on Tablet
(1, 4, 1, NULL, '2025-11-05 08:15:00', '2025-11-05 09:50:00', 100.00),

-- Profile 2 partially watched Episode 4 of Content 6
(2, 2, 6, 4, '2025-11-01 17:00:00', NULL, 35.00),

-- Profile 3 completed Episode 7 of Content 8
(3, 3, 8, 7, '2025-11-05 23:00:00', '2025-11-06 00:00:00', 100.00);



SELECT 
    device_type,
    COUNT(*) AS total_watches,
    ROUND(AVG(completion_percentage), 2) AS avg_completion
FROM (
    SELECT 
        da.completion_percentage,
        CASE
            WHEN dv.device_name LIKE '%Phone%' OR dv.device_name LIKE '%Pixel%' THEN 'Mobile'
            WHEN dv.device_name LIKE '%TV%' THEN 'Smart TV'
            WHEN dv.device_name LIKE '%Laptop%' THEN 'Laptop'
            WHEN dv.device_name LIKE '%Tablet%' THEN 'Tablet'
            ELSE 'Other'
        END AS device_type
    FROM Device_Activity da
    JOIN Device dv ON da.device_id = dv.device_id
) AS categorized
GROUP BY device_type
ORDER BY total_watches DESC;

WITH categorized AS (
    SELECT 
        da.content_id,
        da.completion_percentage,
        CASE
            WHEN dv.device_name LIKE '%Phone%' OR dv.device_name LIKE '%Pixel%' THEN 'Mobile'
            WHEN dv.device_name LIKE '%TV%' THEN 'Smart TV'
            WHEN dv.device_name LIKE '%Laptop%' THEN 'Laptop'
            WHEN dv.device_name LIKE '%Tablet%' THEN 'Tablet'
            ELSE 'Other'
        END AS device_type
    FROM Device_Activity da
    JOIN Device dv ON da.device_id = dv.device_id
)
SELECT 
    g.device_type,
    g.total_watches,
    g.avg_completion,
    (
        SELECT c.title
        FROM categorized c2
        JOIN Content c ON c2.content_id = c.content_id
        WHERE c2.device_type = g.device_type
        GROUP BY c2.content_id
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) AS most_watched_content
FROM (
    SELECT 
        device_type,
        COUNT(*) AS total_watches,
        ROUND(AVG(completion_percentage), 2) AS avg_completion
    FROM categorized
    GROUP BY device_type
) AS g
ORDER BY g.total_watches DESC;





