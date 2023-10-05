CREATE TABLE image2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score FLOAT,
    idVideo INTEGER NOT NULL,
    selected BOOLEAN DEFAULT 0,
    timestamp INTEGER DEFAULT 0,
    nameImage TEXT,
    FOREIGN KEY (idVideo) REFERENCES "video1"(id)
);

INSERT INTO image2 SELECT * FROM image;

DROP table image;

ALTER TABLE image2 RENAME TO image;

delete from center;
delete from sqlite_sequence where name='center';

delete from video;
delete from sqlite_sequence where name='video';

delete from user;
delete from sqlite_sequence where name='user';

delete from annotation;