CREATE TABLE "user" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
"username" varchar(255) NOT NULL,
"email" varchar(255),
"password" varchar(120) NOT NULL,
"salt" varchar(32) NOT NULL,
"active" bool NOT NULL DEFAULT true,
PRIMARY KEY ("id") 
);

CREATE UNIQUE INDEX "user_username_index" ON "user" ("username");

CREATE TABLE "base" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
PRIMARY KEY ("id") 
);

CREATE TABLE "role" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
"name" varchar(80) NOT NULL,
"description" varchar(255) NOT NULL,
PRIMARY KEY ("id") 
);

CREATE TABLE "roles_users" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"user_id" int8 NOT NULL,
"role_id" int8 NOT NULL,
PRIMARY KEY ("id") 
);

CREATE TABLE "post" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
"parent_id" int8,
"author_id" int8 NOT NULL,
"active" bool NOT NULL DEFAULT false,
"published" timestamptz,
"title" varchar(255) NOT NULL,
"subtitle" varchar(255),
"slug" varchar(255) NOT NULL,
"format" post_content_format_enum NOT NULL,
"version" int4 NOT NULL,
"domain" varchar(255) NOT NULL,
"location" varchar(255) NOT NULL,
"score" int8,
PRIMARY KEY ("id") 
);

CREATE UNIQUE INDEX "post_slug_index" ON "post" ("slug");

CREATE TABLE "comment" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
"post_id" int8 NOT NULL,
"parent_id" int8,
"author_id" int8 NOT NULL,
"score" int8,
PRIMARY KEY ("id") 
);

CREATE TABLE "post_raiting" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
"raiter_id" int8 NOT NULL,
"raiting" int8 NOT NULL,
"post_id" int8 NOT NULL,
PRIMARY KEY ("id") 
);

CREATE TABLE "comment_raiting" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
"raiter_id" int8 NOT NULL,
"raiting" int8 NOT NULL,
"comment_id" int8 NOT NULL,
PRIMARY KEY ("id") 
);

CREATE TABLE "tag" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"modified" timestamptz NOT NULL,
"slug" varchar(255) NOT NULL,
PRIMARY KEY ("id") 
);

CREATE TABLE "post_tag" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"tag_id" int8 NOT NULL,
"post_id" int8 NOT NULL,
PRIMARY KEY ("id") 
);

CREATE TABLE "comment_tag" (
"id" serial8 NOT NULL,
"created" timestamptz NOT NULL,
"tag_id" int8 NOT NULL,
"comment_id" int8 NOT NULL,
PRIMARY KEY ("id") 
);


ALTER TABLE "roles_users" ADD CONSTRAINT "roles_users_user_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "user" ("id");
ALTER TABLE "roles_users" ADD CONSTRAINT "roles_users_role_role_id_fk" FOREIGN KEY ("role_id") REFERENCES "role" ("id");
ALTER TABLE "post" ADD CONSTRAINT "post_parent_id_post_id_fk" FOREIGN KEY ("parent_id") REFERENCES "post" ("id");
ALTER TABLE "post" ADD CONSTRAINT "post_author_id_user_id_fk" FOREIGN KEY ("author_id") REFERENCES "user" ("id");
ALTER TABLE "comment" ADD CONSTRAINT "comment_post_id_post_id_fk" FOREIGN KEY ("post_id") REFERENCES "post" ("id");
ALTER TABLE "comment" ADD CONSTRAINT "comment_parent_id_comment_id_fk" FOREIGN KEY ("parent_id") REFERENCES "comment" ("id");
ALTER TABLE "comment" ADD CONSTRAINT "comment_author_id_user_id_fk" FOREIGN KEY ("author_id") REFERENCES "user" ("id");
ALTER TABLE "post_raiting" ADD CONSTRAINT "post_raiting_raiter_id_usre_id_fk" FOREIGN KEY ("raiter_id") REFERENCES "user" ("id");
ALTER TABLE "post_raiting" ADD CONSTRAINT "post_raiting_post_id_post_id_fk" FOREIGN KEY ("post_id") REFERENCES "post" ("id");
ALTER TABLE "comment_raiting" ADD CONSTRAINT "comment_raiting_raiter_id_user_id_fk" FOREIGN KEY ("raiter_id") REFERENCES "user" ("id");
ALTER TABLE "comment_raiting" ADD CONSTRAINT "comment_raiting_comment_id_comment_id_fk" FOREIGN KEY ("comment_id") REFERENCES "comment" ("id");
ALTER TABLE "post_tag" ADD CONSTRAINT "post_tag_tag_id_tag_id_fk" FOREIGN KEY ("tag_id") REFERENCES "tag" ("id");
ALTER TABLE "post_tag" ADD CONSTRAINT "post_tag_post_id_post_id_fk" FOREIGN KEY ("post_id") REFERENCES "post" ("id");
ALTER TABLE "comment_tag" ADD CONSTRAINT "comment_tag_comment_id_comment_id_fk" FOREIGN KEY ("comment_id") REFERENCES "comment" ("id");
ALTER TABLE "comment_tag" ADD CONSTRAINT "comment_tag_tag_id_tag_id_fk" FOREIGN KEY ("tag_id") REFERENCES "tag" ("id");

