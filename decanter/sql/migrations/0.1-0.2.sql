CREATE TABLE "image" (
    "id" serial8 NOT NULL,
    "created" timestamptz NOT NULL,
    "modified" timestamptz NOT NULL,
    "post_id" int8,
    "name" varchar(255) NOT NULL,
    "alt" varchar(255),
    "domain" varchar(255) NOT NULL,
    "location" varchar(255) NOT NULL,
    "thumbnail" varchar(255),
    PRIMARY KEY ("id") 
);

CREATE UNIQUE INDEX "image_name_index" ON "image" ("name");
ALTER TABLE "image" ADD CONSTRAINT "image_post_id_post_id_fk" FOREIGN KEY ("post_id") REFERENCES "post" ("id");
