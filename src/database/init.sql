--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-12-25 13:07:01

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 39066)
-- Name: public; Type: SCHEMA; Schema: -; Owner: admin
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO admin;

--
-- TOC entry 5100 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: admin
--

COMMENT ON SCHEMA public IS '';


--
-- TOC entry 2 (class 3079 OID 39067)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5102 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 39134)
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    action character varying NOT NULL,
    details text,
    ip_address character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.activity_logs OWNER TO admin;

--
-- TOC entry 222 (class 1259 OID 39133)
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_logs_id_seq OWNER TO admin;

--
-- TOC entry 5103 (class 0 OID 0)
-- Dependencies: 222
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


--
-- TOC entry 227 (class 1259 OID 39169)
-- Name: districts; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.districts (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.districts OWNER TO admin;

--
-- TOC entry 226 (class 1259 OID 39168)
-- Name: districts_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.districts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.districts_id_seq OWNER TO admin;

--
-- TOC entry 5104 (class 0 OID 0)
-- Dependencies: 226
-- Name: districts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.districts_id_seq OWNED BY public.districts.id;


--
-- TOC entry 235 (class 1259 OID 39244)
-- Name: hotels; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.hotels (
    place_id integer NOT NULL,
    star_rating integer,
    price_per_night numeric(10,2),
    check_in_time time without time zone,
    check_out_time time without time zone
);


ALTER TABLE public.hotels OWNER TO admin;

--
-- TOC entry 233 (class 1259 OID 39217)
-- Name: place_images; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.place_images (
    id integer NOT NULL,
    place_id integer NOT NULL,
    image_url character varying NOT NULL,
    is_main boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.place_images OWNER TO admin;

--
-- TOC entry 232 (class 1259 OID 39216)
-- Name: place_images_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.place_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.place_images_id_seq OWNER TO admin;

--
-- TOC entry 5105 (class 0 OID 0)
-- Dependencies: 232
-- Name: place_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.place_images_id_seq OWNED BY public.place_images.id;


--
-- TOC entry 229 (class 1259 OID 39178)
-- Name: place_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.place_types (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.place_types OWNER TO admin;

--
-- TOC entry 228 (class 1259 OID 39177)
-- Name: place_types_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.place_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.place_types_id_seq OWNER TO admin;

--
-- TOC entry 5106 (class 0 OID 0)
-- Dependencies: 228
-- Name: place_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.place_types_id_seq OWNED BY public.place_types.id;


--
-- TOC entry 231 (class 1259 OID 39187)
-- Name: places; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.places (
    id integer NOT NULL,
    place_type_id integer NOT NULL,
    district_id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    address_detail character varying,
    latitude numeric(9,6) NOT NULL,
    longitude numeric(9,6) NOT NULL,
    rating_average numeric(3,2) DEFAULT 0,
    rating_count integer DEFAULT 0,
    rating_total numeric(10,2) DEFAULT 0,
    open_hour time without time zone,
    close_hour time without time zone,
    price_min numeric(10,2) DEFAULT 0,
    price_max numeric(10,2) DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone
);


ALTER TABLE public.places OWNER TO admin;

--
-- TOC entry 230 (class 1259 OID 39186)
-- Name: places_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.places_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.places_id_seq OWNER TO admin;

--
-- TOC entry 5107 (class 0 OID 0)
-- Dependencies: 230
-- Name: places_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.places_id_seq OWNED BY public.places.id;


--
-- TOC entry 234 (class 1259 OID 39232)
-- Name: restaurants; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.restaurants (
    place_id integer NOT NULL,
    cuisine_type character varying,
    avg_price_per_person numeric(10,2)
);


ALTER TABLE public.restaurants OWNER TO admin;

--
-- TOC entry 219 (class 1259 OID 39105)
-- Name: roles; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    role_name character varying(50) NOT NULL
);


ALTER TABLE public.roles OWNER TO admin;

--
-- TOC entry 218 (class 1259 OID 39104)
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO admin;

--
-- TOC entry 5108 (class 0 OID 0)
-- Dependencies: 218
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- TOC entry 225 (class 1259 OID 39150)
-- Name: token_refresh; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.token_refresh (
    id integer NOT NULL,
    user_id integer NOT NULL,
    refresh_token character varying NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    revoked boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.token_refresh OWNER TO admin;

--
-- TOC entry 224 (class 1259 OID 39149)
-- Name: token_refresh_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.token_refresh_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.token_refresh_id_seq OWNER TO admin;

--
-- TOC entry 5109 (class 0 OID 0)
-- Dependencies: 224
-- Name: token_refresh_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.token_refresh_id_seq OWNED BY public.token_refresh.id;


--
-- TOC entry 236 (class 1259 OID 39254)
-- Name: tourist_attractions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.tourist_attractions (
    place_id integer NOT NULL,
    ticket_price numeric(10,2),
    is_ticket_required boolean DEFAULT true
);


ALTER TABLE public.tourist_attractions OWNER TO admin;

--
-- TOC entry 237 (class 1259 OID 39265)
-- Name: user_place_favorites; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_place_favorites (
    user_id integer NOT NULL,
    place_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_place_favorites OWNER TO admin;

--
-- TOC entry 238 (class 1259 OID 39281)
-- Name: user_post_favorites; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_post_favorites (
    user_id integer NOT NULL,
    post_id character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_post_favorites OWNER TO admin;

--
-- TOC entry 221 (class 1259 OID 39114)
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    full_name character varying NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    avatar_url character varying,
    bio character varying,
    reputation_score integer DEFAULT 0,
    is_active boolean DEFAULT true,
    ban_reason character varying,
    deleted_at timestamp without time zone,
    role_id integer NOT NULL,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO admin;

--
-- TOC entry 220 (class 1259 OID 39113)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO admin;

--
-- TOC entry 5110 (class 0 OID 0)
-- Dependencies: 220
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 240 (class 1259 OID 39290)
-- Name: visit_logs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.visit_logs (
    id integer NOT NULL,
    user_id integer,
    place_id integer,
    post_id character varying,
    page_url character varying,
    ip_address character varying,
    user_agent text,
    visited_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.visit_logs OWNER TO admin;

--
-- TOC entry 239 (class 1259 OID 39289)
-- Name: visit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.visit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.visit_logs_id_seq OWNER TO admin;

--
-- TOC entry 5111 (class 0 OID 0)
-- Dependencies: 239
-- Name: visit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.visit_logs_id_seq OWNED BY public.visit_logs.id;


--
-- TOC entry 4845 (class 2604 OID 39137)
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


--
-- TOC entry 4850 (class 2604 OID 39172)
-- Name: districts id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.districts ALTER COLUMN id SET DEFAULT nextval('public.districts_id_seq'::regclass);


--
-- TOC entry 4860 (class 2604 OID 39220)
-- Name: place_images id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.place_images ALTER COLUMN id SET DEFAULT nextval('public.place_images_id_seq'::regclass);


--
-- TOC entry 4851 (class 2604 OID 39181)
-- Name: place_types id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.place_types ALTER COLUMN id SET DEFAULT nextval('public.place_types_id_seq'::regclass);


--
-- TOC entry 4852 (class 2604 OID 39190)
-- Name: places id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.places ALTER COLUMN id SET DEFAULT nextval('public.places_id_seq'::regclass);


--
-- TOC entry 4839 (class 2604 OID 39108)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 4847 (class 2604 OID 39153)
-- Name: token_refresh id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.token_refresh ALTER COLUMN id SET DEFAULT nextval('public.token_refresh_id_seq'::regclass);


--
-- TOC entry 4840 (class 2604 OID 39117)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4866 (class 2604 OID 39293)
-- Name: visit_logs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.visit_logs ALTER COLUMN id SET DEFAULT nextval('public.visit_logs_id_seq'::regclass);


--
-- TOC entry 5077 (class 0 OID 39134)
-- Dependencies: 223
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- TOC entry 5081 (class 0 OID 39169)
-- Dependencies: 227
-- Data for Name: districts; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.districts VALUES (1, 'Hoàn Kiếm');
INSERT INTO public.districts VALUES (2, 'Ba Đình');
INSERT INTO public.districts VALUES (3, 'Tây Hồ');
INSERT INTO public.districts VALUES (4, 'Hai Bà Trưng');
INSERT INTO public.districts VALUES (5, 'Đống Đa');
INSERT INTO public.districts VALUES (6, 'Cầu Giấy');
INSERT INTO public.districts VALUES (7, 'Thanh Xuân');
INSERT INTO public.districts VALUES (8, 'Hoàng Mai');
INSERT INTO public.districts VALUES (9, 'Long Biên');
INSERT INTO public.districts VALUES (10, 'Nam Từ Liêm');
INSERT INTO public.districts VALUES (11, 'Bắc Từ Liêm');
INSERT INTO public.districts VALUES (12, 'Hà Đông');
INSERT INTO public.districts VALUES (13, 'Sơn Tây');
INSERT INTO public.districts VALUES (14, 'Gia Lâm');
INSERT INTO public.districts VALUES (15, 'Mỹ Đức');
INSERT INTO public.districts VALUES (16, 'Sóc Sơn');


--
-- TOC entry 5089 (class 0 OID 39244)
-- Dependencies: 235
-- Data for Name: hotels; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.hotels VALUES (81, 5, 6000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (82, 5, 6000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (83, 5, 6000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (84, 5, 6000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (85, 5, 6000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (86, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (87, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (88, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (89, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (90, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (91, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (92, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (93, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (94, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (95, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (96, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (97, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (98, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (99, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (100, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (101, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (102, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (103, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (104, 3, 500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (105, 4, 500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (106, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (107, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (108, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (109, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (110, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (111, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (112, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (113, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (114, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (115, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (116, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (117, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (118, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (119, 5, 3000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (120, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (121, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (122, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (123, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (124, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (125, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (126, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (127, 5, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (128, 5, 6000000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (129, 4, 1500000.00, '14:00:00', '12:00:00');
INSERT INTO public.hotels VALUES (130, 3, 500000.00, '14:00:00', '12:00:00');


--
-- TOC entry 5087 (class 0 OID 39217)
-- Dependencies: 233
-- Data for Name: place_images; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.place_images VALUES (1, 1, '/static/uploads/places/place_1_0.jpg', true, '2025-12-25 12:18:43.640352');
INSERT INTO public.place_images VALUES (2, 1, '/static/uploads/places/place_1_1.jpg', false, '2025-12-25 12:18:43.640352');
INSERT INTO public.place_images VALUES (3, 1, '/static/uploads/places/place_1_2.jpg', false, '2025-12-25 12:18:43.640352');
INSERT INTO public.place_images VALUES (4, 2, '/static/uploads/places/place_2_0.jpg', true, '2025-12-25 12:18:45.214182');
INSERT INTO public.place_images VALUES (5, 2, '/static/uploads/places/place_2_1.jpg', false, '2025-12-25 12:18:45.214182');
INSERT INTO public.place_images VALUES (6, 2, '/static/uploads/places/place_2_2.jpg', false, '2025-12-25 12:18:45.214182');
INSERT INTO public.place_images VALUES (7, 3, '/static/uploads/places/place_3_0.jpg', true, '2025-12-25 12:18:45.861857');
INSERT INTO public.place_images VALUES (8, 3, '/static/uploads/places/place_3_1.jpg', false, '2025-12-25 12:18:45.861857');
INSERT INTO public.place_images VALUES (9, 3, '/static/uploads/places/place_3_2.jpg', false, '2025-12-25 12:18:45.861857');
INSERT INTO public.place_images VALUES (10, 4, '/static/uploads/places/place_4_0.jpg', true, '2025-12-25 12:18:46.386998');
INSERT INTO public.place_images VALUES (11, 4, '/static/uploads/places/place_4_1.jpg', false, '2025-12-25 12:18:46.386998');
INSERT INTO public.place_images VALUES (12, 4, '/static/uploads/places/place_4_2.jpg', false, '2025-12-25 12:18:46.386998');
INSERT INTO public.place_images VALUES (13, 5, '/static/uploads/places/place_5_0.jpg', true, '2025-12-25 12:18:52.212998');
INSERT INTO public.place_images VALUES (14, 5, '/static/uploads/places/place_5_1.png', false, '2025-12-25 12:18:52.212998');
INSERT INTO public.place_images VALUES (15, 5, '/static/uploads/places/place_5_2.jpg', false, '2025-12-25 12:18:52.212998');
INSERT INTO public.place_images VALUES (16, 6, '/static/uploads/places/place_6_0.jpg', true, '2025-12-25 12:18:55.558672');
INSERT INTO public.place_images VALUES (17, 6, '/static/uploads/places/place_6_1.jpg', false, '2025-12-25 12:18:55.558672');
INSERT INTO public.place_images VALUES (18, 6, '/static/uploads/places/place_6_2.jpeg', false, '2025-12-25 12:18:55.558672');
INSERT INTO public.place_images VALUES (19, 7, '/static/uploads/places/place_7_0.jpg', true, '2025-12-25 12:18:58.523194');
INSERT INTO public.place_images VALUES (20, 7, '/static/uploads/places/place_7_1.jpg', false, '2025-12-25 12:18:58.523194');
INSERT INTO public.place_images VALUES (21, 7, '/static/uploads/places/place_7_2.png', false, '2025-12-25 12:18:58.523194');
INSERT INTO public.place_images VALUES (22, 8, '/static/uploads/places/place_8_0.jpg', true, '2025-12-25 12:19:01.013612');
INSERT INTO public.place_images VALUES (23, 8, '/static/uploads/places/place_8_1.jpg', false, '2025-12-25 12:19:01.013612');
INSERT INTO public.place_images VALUES (24, 8, '/static/uploads/places/place_8_2.jpg', false, '2025-12-25 12:19:01.013612');
INSERT INTO public.place_images VALUES (25, 9, '/static/uploads/places/place_9_0.jpeg', true, '2025-12-25 12:19:03.614342');
INSERT INTO public.place_images VALUES (26, 9, '/static/uploads/places/place_9_1.jpg', false, '2025-12-25 12:19:03.614342');
INSERT INTO public.place_images VALUES (27, 9, '/static/uploads/places/place_9_2.jpg', false, '2025-12-25 12:19:03.614342');
INSERT INTO public.place_images VALUES (28, 10, '/static/uploads/places/place_10_0.jpg', true, '2025-12-25 12:19:04.128635');
INSERT INTO public.place_images VALUES (29, 10, '/static/uploads/places/place_10_1.jpg', false, '2025-12-25 12:19:04.128635');
INSERT INTO public.place_images VALUES (30, 10, '/static/uploads/places/place_10_2.jpg', false, '2025-12-25 12:19:04.128635');
INSERT INTO public.place_images VALUES (31, 11, '/static/uploads/places/place_11_0.jpg', true, '2025-12-25 12:19:07.306288');
INSERT INTO public.place_images VALUES (32, 11, '/static/uploads/places/place_11_1.jpg', false, '2025-12-25 12:19:07.306288');
INSERT INTO public.place_images VALUES (33, 11, '/static/uploads/places/place_11_2.jpg', false, '2025-12-25 12:19:07.306288');
INSERT INTO public.place_images VALUES (34, 12, '/static/uploads/places/place_12_0.jpg', true, '2025-12-25 12:19:08.986994');
INSERT INTO public.place_images VALUES (35, 12, '/static/uploads/places/place_12_1.jpg', false, '2025-12-25 12:19:08.986994');
INSERT INTO public.place_images VALUES (36, 12, '/static/uploads/places/place_12_2.jpg', false, '2025-12-25 12:19:08.986994');
INSERT INTO public.place_images VALUES (37, 13, '/static/uploads/places/place_13_0.jpg', true, '2025-12-25 12:19:11.789567');
INSERT INTO public.place_images VALUES (38, 13, '/static/uploads/places/place_13_1.jpg', false, '2025-12-25 12:19:11.789567');
INSERT INTO public.place_images VALUES (39, 13, '/static/uploads/places/place_13_2.jpg', false, '2025-12-25 12:19:11.789567');
INSERT INTO public.place_images VALUES (40, 14, '/static/uploads/places/place_14_0.jpg', true, '2025-12-25 12:19:21.67688');
INSERT INTO public.place_images VALUES (41, 14, '/static/uploads/places/place_14_1.jpg', false, '2025-12-25 12:19:21.67688');
INSERT INTO public.place_images VALUES (42, 14, '/static/uploads/places/place_14_2.jpg', false, '2025-12-25 12:19:21.67688');
INSERT INTO public.place_images VALUES (43, 15, '/static/uploads/places/place_15_0.jpg', true, '2025-12-25 12:19:25.182978');
INSERT INTO public.place_images VALUES (44, 15, '/static/uploads/places/place_15_1.jpg', false, '2025-12-25 12:19:25.182978');
INSERT INTO public.place_images VALUES (45, 15, '/static/uploads/places/place_15_2.jpg', false, '2025-12-25 12:19:25.182978');
INSERT INTO public.place_images VALUES (46, 16, '/static/uploads/places/place_16_0.jpg', true, '2025-12-25 12:19:28.261463');
INSERT INTO public.place_images VALUES (47, 16, '/static/uploads/places/place_16_1.jpg', false, '2025-12-25 12:19:28.261463');
INSERT INTO public.place_images VALUES (48, 16, '/static/uploads/places/place_16_2.jpg', false, '2025-12-25 12:19:28.261463');
INSERT INTO public.place_images VALUES (49, 17, '/static/uploads/places/place_17_0.jpg', true, '2025-12-25 12:19:29.885371');
INSERT INTO public.place_images VALUES (50, 17, '/static/uploads/places/place_17_1.jpg', false, '2025-12-25 12:19:29.885371');
INSERT INTO public.place_images VALUES (51, 17, '/static/uploads/places/place_17_2.jpeg', false, '2025-12-25 12:19:29.885371');
INSERT INTO public.place_images VALUES (52, 18, '/static/uploads/places/place_18_0.jpg', true, '2025-12-25 12:19:34.114869');
INSERT INTO public.place_images VALUES (53, 18, '/static/uploads/places/place_18_1.jpeg', false, '2025-12-25 12:19:34.114869');
INSERT INTO public.place_images VALUES (54, 18, '/static/uploads/places/place_18_2.jpg', false, '2025-12-25 12:19:34.114869');
INSERT INTO public.place_images VALUES (55, 19, '/static/uploads/places/place_19_0.jpg', true, '2025-12-25 12:19:36.881885');
INSERT INTO public.place_images VALUES (56, 19, '/static/uploads/places/place_19_1.jpeg', false, '2025-12-25 12:19:36.881885');
INSERT INTO public.place_images VALUES (57, 19, '/static/uploads/places/place_19_2.jpg', false, '2025-12-25 12:19:36.881885');
INSERT INTO public.place_images VALUES (58, 20, '/static/uploads/places/place_20_0.jpg', true, '2025-12-25 12:19:44.212577');
INSERT INTO public.place_images VALUES (59, 20, '/static/uploads/places/place_20_1.jpg', false, '2025-12-25 12:19:44.212577');
INSERT INTO public.place_images VALUES (60, 20, '/static/uploads/places/place_20_2.jpg', false, '2025-12-25 12:19:44.212577');
INSERT INTO public.place_images VALUES (61, 21, '/static/uploads/places/place_21_0.jpg', true, '2025-12-25 12:19:46.841741');
INSERT INTO public.place_images VALUES (62, 21, '/static/uploads/places/place_21_1.jpg', false, '2025-12-25 12:19:46.841741');
INSERT INTO public.place_images VALUES (63, 21, '/static/uploads/places/place_21_2.jpg', false, '2025-12-25 12:19:46.841741');
INSERT INTO public.place_images VALUES (64, 22, '/static/uploads/places/place_22_0.jpg', true, '2025-12-25 12:19:49.468881');
INSERT INTO public.place_images VALUES (65, 23, '/static/uploads/places/place_23_0.jpg', true, '2025-12-25 12:19:50.990489');
INSERT INTO public.place_images VALUES (66, 23, '/static/uploads/places/place_23_1.jpg', false, '2025-12-25 12:19:50.990489');
INSERT INTO public.place_images VALUES (67, 24, '/static/uploads/places/place_24_0.jpg', true, '2025-12-25 12:19:52.4965');
INSERT INTO public.place_images VALUES (68, 24, '/static/uploads/places/place_24_1.jpg', false, '2025-12-25 12:19:52.4965');
INSERT INTO public.place_images VALUES (69, 24, '/static/uploads/places/place_24_2.jpg', false, '2025-12-25 12:19:52.4965');
INSERT INTO public.place_images VALUES (70, 25, '/static/uploads/places/place_25_0.jpg', true, '2025-12-25 12:19:56.714116');
INSERT INTO public.place_images VALUES (71, 25, '/static/uploads/places/place_25_1.jpg', false, '2025-12-25 12:19:56.714116');
INSERT INTO public.place_images VALUES (72, 25, '/static/uploads/places/place_25_2.jpg', false, '2025-12-25 12:19:56.714116');
INSERT INTO public.place_images VALUES (73, 26, '/static/uploads/places/place_26_0.png', true, '2025-12-25 12:19:57.847635');
INSERT INTO public.place_images VALUES (74, 26, '/static/uploads/places/place_26_1.jpg', false, '2025-12-25 12:19:57.847635');
INSERT INTO public.place_images VALUES (75, 26, '/static/uploads/places/place_26_2.jpg', false, '2025-12-25 12:19:57.847635');
INSERT INTO public.place_images VALUES (76, 27, '/static/uploads/places/place_27_0.jpg', true, '2025-12-25 12:20:04.031346');
INSERT INTO public.place_images VALUES (77, 27, '/static/uploads/places/place_27_1.jpg', false, '2025-12-25 12:20:04.031346');
INSERT INTO public.place_images VALUES (78, 27, '/static/uploads/places/place_27_2.jpg', false, '2025-12-25 12:20:04.031346');
INSERT INTO public.place_images VALUES (79, 28, '/static/uploads/places/place_28_0.jpg', true, '2025-12-25 12:20:06.4362');
INSERT INTO public.place_images VALUES (80, 28, '/static/uploads/places/place_28_1.jpeg', false, '2025-12-25 12:20:06.4362');
INSERT INTO public.place_images VALUES (81, 28, '/static/uploads/places/place_28_2.jpg', false, '2025-12-25 12:20:06.4362');
INSERT INTO public.place_images VALUES (82, 29, '/static/uploads/places/place_29_0.jpg', true, '2025-12-25 12:20:09.662124');
INSERT INTO public.place_images VALUES (83, 29, '/static/uploads/places/place_29_1.jpg', false, '2025-12-25 12:20:09.662124');
INSERT INTO public.place_images VALUES (84, 31, '/static/uploads/places/place_31_0.jpg', true, '2025-12-25 12:20:12.905975');
INSERT INTO public.place_images VALUES (85, 31, '/static/uploads/places/place_31_1.jpg', false, '2025-12-25 12:20:12.905975');
INSERT INTO public.place_images VALUES (86, 31, '/static/uploads/places/place_31_2.jpg', false, '2025-12-25 12:20:12.905975');
INSERT INTO public.place_images VALUES (87, 32, '/static/uploads/places/place_32_0.jpg', true, '2025-12-25 12:20:13.773335');
INSERT INTO public.place_images VALUES (88, 32, '/static/uploads/places/place_32_1.jpg', false, '2025-12-25 12:20:13.773335');
INSERT INTO public.place_images VALUES (89, 32, '/static/uploads/places/place_32_2.jpg', false, '2025-12-25 12:20:13.773335');
INSERT INTO public.place_images VALUES (90, 33, '/static/uploads/places/place_33_0.png', true, '2025-12-25 12:20:16.846484');
INSERT INTO public.place_images VALUES (91, 33, '/static/uploads/places/place_33_1.jpg', false, '2025-12-25 12:20:16.846484');
INSERT INTO public.place_images VALUES (92, 33, '/static/uploads/places/place_33_2.jpg', false, '2025-12-25 12:20:16.846484');
INSERT INTO public.place_images VALUES (93, 34, '/static/uploads/places/place_34_0.jpg', true, '2025-12-25 12:20:19.698269');
INSERT INTO public.place_images VALUES (94, 34, '/static/uploads/places/place_34_1.jpg', false, '2025-12-25 12:20:19.698269');
INSERT INTO public.place_images VALUES (95, 34, '/static/uploads/places/place_34_2.jpg', false, '2025-12-25 12:20:19.698269');
INSERT INTO public.place_images VALUES (96, 35, '/static/uploads/places/place_35_0.jpg', true, '2025-12-25 12:20:26.232432');
INSERT INTO public.place_images VALUES (97, 35, '/static/uploads/places/place_35_1.jpg', false, '2025-12-25 12:20:26.232432');
INSERT INTO public.place_images VALUES (98, 35, '/static/uploads/places/place_35_2.jpg', false, '2025-12-25 12:20:26.232432');
INSERT INTO public.place_images VALUES (99, 36, '/static/uploads/places/place_36_0.jpg', true, '2025-12-25 12:20:29.642791');
INSERT INTO public.place_images VALUES (100, 36, '/static/uploads/places/place_36_1.jpg', false, '2025-12-25 12:20:29.642791');
INSERT INTO public.place_images VALUES (101, 36, '/static/uploads/places/place_36_2.jpg', false, '2025-12-25 12:20:29.642791');
INSERT INTO public.place_images VALUES (102, 37, '/static/uploads/places/place_37_0.jpg', true, '2025-12-25 12:20:30.944552');
INSERT INTO public.place_images VALUES (103, 37, '/static/uploads/places/place_37_1.jpg', false, '2025-12-25 12:20:30.944552');
INSERT INTO public.place_images VALUES (104, 37, '/static/uploads/places/place_37_2.jpg', false, '2025-12-25 12:20:30.944552');
INSERT INTO public.place_images VALUES (105, 38, '/static/uploads/places/place_38_0.jpg', true, '2025-12-25 12:20:32.706396');
INSERT INTO public.place_images VALUES (106, 38, '/static/uploads/places/place_38_1.jpg', false, '2025-12-25 12:20:32.706396');
INSERT INTO public.place_images VALUES (107, 38, '/static/uploads/places/place_38_2.jpg', false, '2025-12-25 12:20:32.706396');
INSERT INTO public.place_images VALUES (108, 39, '/static/uploads/places/place_39_0.jpg', true, '2025-12-25 12:20:34.31271');
INSERT INTO public.place_images VALUES (109, 39, '/static/uploads/places/place_39_1.jpg', false, '2025-12-25 12:20:34.31271');
INSERT INTO public.place_images VALUES (110, 39, '/static/uploads/places/place_39_2.jpg', false, '2025-12-25 12:20:34.31271');
INSERT INTO public.place_images VALUES (111, 40, '/static/uploads/places/place_40_0.jpg', true, '2025-12-25 12:20:35.196248');
INSERT INTO public.place_images VALUES (112, 40, '/static/uploads/places/place_40_1.jpg', false, '2025-12-25 12:20:35.196248');
INSERT INTO public.place_images VALUES (113, 40, '/static/uploads/places/place_40_2.jpg', false, '2025-12-25 12:20:35.196248');
INSERT INTO public.place_images VALUES (114, 41, '/static/uploads/places/place_41_0.jpg', true, '2025-12-25 12:20:36.246824');
INSERT INTO public.place_images VALUES (115, 41, '/static/uploads/places/place_41_1.jpg', false, '2025-12-25 12:20:36.246824');
INSERT INTO public.place_images VALUES (116, 41, '/static/uploads/places/place_41_2.jpg', false, '2025-12-25 12:20:36.246824');
INSERT INTO public.place_images VALUES (117, 42, '/static/uploads/places/place_42_0.jpg', true, '2025-12-25 12:20:41.0463');
INSERT INTO public.place_images VALUES (118, 42, '/static/uploads/places/place_42_1.jpg', false, '2025-12-25 12:20:41.0463');
INSERT INTO public.place_images VALUES (119, 42, '/static/uploads/places/place_42_2.jpg', false, '2025-12-25 12:20:41.0463');
INSERT INTO public.place_images VALUES (120, 43, '/static/uploads/places/place_43_0.jpg', true, '2025-12-25 12:20:44.354042');
INSERT INTO public.place_images VALUES (121, 43, '/static/uploads/places/place_43_1.jpg', false, '2025-12-25 12:20:44.354042');
INSERT INTO public.place_images VALUES (122, 43, '/static/uploads/places/place_43_2.jpg', false, '2025-12-25 12:20:44.354042');
INSERT INTO public.place_images VALUES (123, 44, '/static/uploads/places/place_44_0.jpg', true, '2025-12-25 12:20:48.335922');
INSERT INTO public.place_images VALUES (124, 44, '/static/uploads/places/place_44_1.jpeg', false, '2025-12-25 12:20:48.335922');
INSERT INTO public.place_images VALUES (125, 44, '/static/uploads/places/place_44_2.jpg', false, '2025-12-25 12:20:48.335922');
INSERT INTO public.place_images VALUES (126, 45, '/static/uploads/places/place_45_0.jpg', true, '2025-12-25 12:20:49.397138');
INSERT INTO public.place_images VALUES (127, 45, '/static/uploads/places/place_45_1.jpg', false, '2025-12-25 12:20:49.397138');
INSERT INTO public.place_images VALUES (128, 45, '/static/uploads/places/place_45_2.jpg', false, '2025-12-25 12:20:49.397138');
INSERT INTO public.place_images VALUES (129, 46, '/static/uploads/places/place_46_0.jpg', true, '2025-12-25 12:20:52.255648');
INSERT INTO public.place_images VALUES (130, 46, '/static/uploads/places/place_46_1.jpg', false, '2025-12-25 12:20:52.255648');
INSERT INTO public.place_images VALUES (131, 46, '/static/uploads/places/place_46_2.jpg', false, '2025-12-25 12:20:52.255648');
INSERT INTO public.place_images VALUES (132, 47, '/static/uploads/places/place_47_0.jpg', true, '2025-12-25 12:20:57.420886');
INSERT INTO public.place_images VALUES (133, 47, '/static/uploads/places/place_47_1.jpg', false, '2025-12-25 12:20:57.420886');
INSERT INTO public.place_images VALUES (134, 47, '/static/uploads/places/place_47_2.jpg', false, '2025-12-25 12:20:57.420886');
INSERT INTO public.place_images VALUES (135, 48, '/static/uploads/places/place_48_0.jpg', true, '2025-12-25 12:20:59.176988');
INSERT INTO public.place_images VALUES (136, 48, '/static/uploads/places/place_48_1.jpg', false, '2025-12-25 12:20:59.176988');
INSERT INTO public.place_images VALUES (137, 48, '/static/uploads/places/place_48_2.jpg', false, '2025-12-25 12:20:59.176988');
INSERT INTO public.place_images VALUES (138, 49, '/static/uploads/places/place_49_0.jpg', true, '2025-12-25 12:21:00.757053');
INSERT INTO public.place_images VALUES (139, 49, '/static/uploads/places/place_49_1.jpg', false, '2025-12-25 12:21:00.757053');
INSERT INTO public.place_images VALUES (140, 49, '/static/uploads/places/place_49_2.jpg', false, '2025-12-25 12:21:00.757053');
INSERT INTO public.place_images VALUES (141, 50, '/static/uploads/places/place_50_0.jpg', true, '2025-12-25 12:21:01.168427');
INSERT INTO public.place_images VALUES (142, 50, '/static/uploads/places/place_50_1.jpg', false, '2025-12-25 12:21:01.168427');
INSERT INTO public.place_images VALUES (143, 50, '/static/uploads/places/place_50_2.jpg', false, '2025-12-25 12:21:01.168427');
INSERT INTO public.place_images VALUES (144, 51, '/static/uploads/places/place_51_0.jpg', true, '2025-12-25 12:21:03.464106');
INSERT INTO public.place_images VALUES (145, 51, '/static/uploads/places/place_51_1.jpeg', false, '2025-12-25 12:21:03.464106');
INSERT INTO public.place_images VALUES (146, 52, '/static/uploads/places/place_52_0.jpg', true, '2025-12-25 12:21:07.136898');
INSERT INTO public.place_images VALUES (147, 52, '/static/uploads/places/place_52_1.jpg', false, '2025-12-25 12:21:07.136898');
INSERT INTO public.place_images VALUES (148, 52, '/static/uploads/places/place_52_2.jpg', false, '2025-12-25 12:21:07.136898');
INSERT INTO public.place_images VALUES (149, 53, '/static/uploads/places/place_53_0.jpg', true, '2025-12-25 12:21:15.186042');
INSERT INTO public.place_images VALUES (150, 53, '/static/uploads/places/place_53_1.jpg', false, '2025-12-25 12:21:15.186042');
INSERT INTO public.place_images VALUES (151, 53, '/static/uploads/places/place_53_2.jpg', false, '2025-12-25 12:21:15.186042');
INSERT INTO public.place_images VALUES (152, 54, '/static/uploads/places/place_54_0.jpg', true, '2025-12-25 12:21:22.17953');
INSERT INTO public.place_images VALUES (153, 54, '/static/uploads/places/place_54_1.jpg', false, '2025-12-25 12:21:22.17953');
INSERT INTO public.place_images VALUES (154, 54, '/static/uploads/places/place_54_2.jpg', false, '2025-12-25 12:21:22.17953');
INSERT INTO public.place_images VALUES (155, 55, '/static/uploads/places/place_55_0.jpg', true, '2025-12-25 12:21:27.092143');
INSERT INTO public.place_images VALUES (156, 55, '/static/uploads/places/place_55_1.jpg', false, '2025-12-25 12:21:27.092143');
INSERT INTO public.place_images VALUES (157, 55, '/static/uploads/places/place_55_2.jpg', false, '2025-12-25 12:21:27.092143');
INSERT INTO public.place_images VALUES (158, 56, '/static/uploads/places/place_56_0.jpg', true, '2025-12-25 12:21:27.583956');
INSERT INTO public.place_images VALUES (159, 56, '/static/uploads/places/place_56_1.jpg', false, '2025-12-25 12:21:27.583956');
INSERT INTO public.place_images VALUES (160, 56, '/static/uploads/places/place_56_2.jpg', false, '2025-12-25 12:21:27.583956');
INSERT INTO public.place_images VALUES (161, 57, '/static/uploads/places/place_57_0.jpg', true, '2025-12-25 12:21:30.736515');
INSERT INTO public.place_images VALUES (162, 57, '/static/uploads/places/place_57_1.jpg', false, '2025-12-25 12:21:30.736515');
INSERT INTO public.place_images VALUES (163, 57, '/static/uploads/places/place_57_2.jpg', false, '2025-12-25 12:21:30.736515');
INSERT INTO public.place_images VALUES (164, 58, '/static/uploads/places/place_58_0.jpg', true, '2025-12-25 12:21:34.29487');
INSERT INTO public.place_images VALUES (165, 59, '/static/uploads/places/place_59_0.jpg', true, '2025-12-25 12:21:36.195691');
INSERT INTO public.place_images VALUES (166, 59, '/static/uploads/places/place_59_1.jpg', false, '2025-12-25 12:21:36.195691');
INSERT INTO public.place_images VALUES (167, 59, '/static/uploads/places/place_59_2.jpg', false, '2025-12-25 12:21:36.195691');
INSERT INTO public.place_images VALUES (168, 60, '/static/uploads/places/place_60_0.jpg', true, '2025-12-25 12:21:37.943771');
INSERT INTO public.place_images VALUES (169, 60, '/static/uploads/places/place_60_1.jpg', false, '2025-12-25 12:21:37.943771');
INSERT INTO public.place_images VALUES (170, 61, '/static/uploads/places/place_61_0.png', true, '2025-12-25 12:21:42.232609');
INSERT INTO public.place_images VALUES (171, 61, '/static/uploads/places/place_61_1.png', false, '2025-12-25 12:21:42.232609');
INSERT INTO public.place_images VALUES (172, 61, '/static/uploads/places/place_61_2.png', false, '2025-12-25 12:21:42.232609');
INSERT INTO public.place_images VALUES (173, 62, '/static/uploads/places/place_62_0.jpg', true, '2025-12-25 12:21:44.182019');
INSERT INTO public.place_images VALUES (174, 62, '/static/uploads/places/place_62_1.jpg', false, '2025-12-25 12:21:44.182019');
INSERT INTO public.place_images VALUES (175, 62, '/static/uploads/places/place_62_2.jpg', false, '2025-12-25 12:21:44.182019');
INSERT INTO public.place_images VALUES (176, 63, '/static/uploads/places/place_63_0.jpg', true, '2025-12-25 12:21:47.732222');
INSERT INTO public.place_images VALUES (177, 63, '/static/uploads/places/place_63_1.jpg', false, '2025-12-25 12:21:47.732222');
INSERT INTO public.place_images VALUES (178, 63, '/static/uploads/places/place_63_2.jpg', false, '2025-12-25 12:21:47.732222');
INSERT INTO public.place_images VALUES (179, 64, '/static/uploads/places/place_64_0.jpg', true, '2025-12-25 12:21:51.444137');
INSERT INTO public.place_images VALUES (180, 64, '/static/uploads/places/place_64_1.jpg', false, '2025-12-25 12:21:51.444137');
INSERT INTO public.place_images VALUES (181, 64, '/static/uploads/places/place_64_2.jpg', false, '2025-12-25 12:21:51.444137');
INSERT INTO public.place_images VALUES (182, 65, '/static/uploads/places/place_65_0.jpg', true, '2025-12-25 12:21:53.896812');
INSERT INTO public.place_images VALUES (183, 65, '/static/uploads/places/place_65_1.jpg', false, '2025-12-25 12:21:53.896812');
INSERT INTO public.place_images VALUES (184, 65, '/static/uploads/places/place_65_2.jpg', false, '2025-12-25 12:21:53.896812');
INSERT INTO public.place_images VALUES (185, 66, '/static/uploads/places/place_66_0.jpg', true, '2025-12-25 12:21:55.05531');
INSERT INTO public.place_images VALUES (186, 66, '/static/uploads/places/place_66_1.jpg', false, '2025-12-25 12:21:55.05531');
INSERT INTO public.place_images VALUES (187, 66, '/static/uploads/places/place_66_2.jpg', false, '2025-12-25 12:21:55.05531');
INSERT INTO public.place_images VALUES (188, 67, '/static/uploads/places/place_67_0.jpg', true, '2025-12-25 12:21:57.989564');
INSERT INTO public.place_images VALUES (189, 67, '/static/uploads/places/place_67_1.jpg', false, '2025-12-25 12:21:57.989564');
INSERT INTO public.place_images VALUES (190, 67, '/static/uploads/places/place_67_2.jpg', false, '2025-12-25 12:21:57.989564');
INSERT INTO public.place_images VALUES (191, 68, '/static/uploads/places/place_68_0.jpg', true, '2025-12-25 12:21:59.672521');
INSERT INTO public.place_images VALUES (192, 68, '/static/uploads/places/place_68_1.jpg', false, '2025-12-25 12:21:59.672521');
INSERT INTO public.place_images VALUES (193, 69, '/static/uploads/places/place_69_0.jpg', true, '2025-12-25 12:22:00.635317');
INSERT INTO public.place_images VALUES (194, 69, '/static/uploads/places/place_69_1.jpg', false, '2025-12-25 12:22:00.635317');
INSERT INTO public.place_images VALUES (195, 69, '/static/uploads/places/place_69_2.png', false, '2025-12-25 12:22:00.635317');
INSERT INTO public.place_images VALUES (196, 70, '/static/uploads/places/place_70_0.jpg', true, '2025-12-25 12:22:04.67239');
INSERT INTO public.place_images VALUES (197, 71, '/static/uploads/places/place_71_0.jpg', true, '2025-12-25 12:22:23.393798');
INSERT INTO public.place_images VALUES (198, 71, '/static/uploads/places/place_71_1.jpg', false, '2025-12-25 12:22:23.393798');
INSERT INTO public.place_images VALUES (199, 71, '/static/uploads/places/place_71_2.jpg', false, '2025-12-25 12:22:23.393798');
INSERT INTO public.place_images VALUES (200, 72, '/static/uploads/places/place_72_0.jpg', true, '2025-12-25 12:22:27.055807');
INSERT INTO public.place_images VALUES (201, 72, '/static/uploads/places/place_72_1.jpg', false, '2025-12-25 12:22:27.055807');
INSERT INTO public.place_images VALUES (202, 72, '/static/uploads/places/place_72_2.jpg', false, '2025-12-25 12:22:27.055807');
INSERT INTO public.place_images VALUES (203, 73, '/static/uploads/places/place_73_0.jpg', true, '2025-12-25 12:22:32.878668');
INSERT INTO public.place_images VALUES (204, 73, '/static/uploads/places/place_73_1.jpg', false, '2025-12-25 12:22:32.878668');
INSERT INTO public.place_images VALUES (205, 73, '/static/uploads/places/place_73_2.jpg', false, '2025-12-25 12:22:32.878668');
INSERT INTO public.place_images VALUES (206, 74, '/static/uploads/places/place_74_0.jpg', true, '2025-12-25 12:22:36.979374');
INSERT INTO public.place_images VALUES (207, 74, '/static/uploads/places/place_74_1.jpg', false, '2025-12-25 12:22:36.979374');
INSERT INTO public.place_images VALUES (208, 74, '/static/uploads/places/place_74_2.jpg', false, '2025-12-25 12:22:36.979374');
INSERT INTO public.place_images VALUES (209, 75, '/static/uploads/places/place_75_0.jpg', true, '2025-12-25 12:22:40.110774');
INSERT INTO public.place_images VALUES (210, 75, '/static/uploads/places/place_75_1.jpg', false, '2025-12-25 12:22:40.110774');
INSERT INTO public.place_images VALUES (211, 75, '/static/uploads/places/place_75_2.jpg', false, '2025-12-25 12:22:40.110774');
INSERT INTO public.place_images VALUES (212, 76, '/static/uploads/places/place_76_0.jpg', true, '2025-12-25 12:22:42.150171');
INSERT INTO public.place_images VALUES (213, 76, '/static/uploads/places/place_76_1.jpg', false, '2025-12-25 12:22:42.150171');
INSERT INTO public.place_images VALUES (214, 76, '/static/uploads/places/place_76_2.jpg', false, '2025-12-25 12:22:42.150171');
INSERT INTO public.place_images VALUES (215, 77, '/static/uploads/places/place_77_0.jpg', true, '2025-12-25 12:22:47.014926');
INSERT INTO public.place_images VALUES (216, 77, '/static/uploads/places/place_77_1.jpg', false, '2025-12-25 12:22:47.014926');
INSERT INTO public.place_images VALUES (217, 77, '/static/uploads/places/place_77_2.jpg', false, '2025-12-25 12:22:47.014926');
INSERT INTO public.place_images VALUES (218, 78, '/static/uploads/places/place_78_0.jpeg', true, '2025-12-25 12:22:52.225928');
INSERT INTO public.place_images VALUES (219, 78, '/static/uploads/places/place_78_1.jpeg', false, '2025-12-25 12:22:52.225928');
INSERT INTO public.place_images VALUES (220, 78, '/static/uploads/places/place_78_2.jpeg', false, '2025-12-25 12:22:52.225928');
INSERT INTO public.place_images VALUES (221, 79, '/static/uploads/places/place_79_0.jpg', true, '2025-12-25 12:22:57.122551');
INSERT INTO public.place_images VALUES (222, 79, '/static/uploads/places/place_79_1.jpg', false, '2025-12-25 12:22:57.122551');
INSERT INTO public.place_images VALUES (223, 79, '/static/uploads/places/place_79_2.jpg', false, '2025-12-25 12:22:57.122551');
INSERT INTO public.place_images VALUES (224, 80, '/static/uploads/places/place_80_0.jpg', true, '2025-12-25 12:22:59.23224');
INSERT INTO public.place_images VALUES (225, 80, '/static/uploads/places/place_80_1.jpg', false, '2025-12-25 12:22:59.23224');
INSERT INTO public.place_images VALUES (226, 80, '/static/uploads/places/place_80_2.jpg', false, '2025-12-25 12:22:59.23224');
INSERT INTO public.place_images VALUES (227, 81, '/static/uploads/places/place_81_0.jpg', true, '2025-12-25 12:23:00.597074');
INSERT INTO public.place_images VALUES (228, 81, '/static/uploads/places/place_81_1.jpg', false, '2025-12-25 12:23:00.597074');
INSERT INTO public.place_images VALUES (229, 81, '/static/uploads/places/place_81_2.jpg', false, '2025-12-25 12:23:00.597074');
INSERT INTO public.place_images VALUES (230, 82, '/static/uploads/places/place_82_0.jpg', true, '2025-12-25 12:23:12.956082');
INSERT INTO public.place_images VALUES (231, 82, '/static/uploads/places/place_82_1.jpg', false, '2025-12-25 12:23:12.956082');
INSERT INTO public.place_images VALUES (232, 82, '/static/uploads/places/place_82_2.jpg', false, '2025-12-25 12:23:12.956082');
INSERT INTO public.place_images VALUES (233, 83, '/static/uploads/places/place_83_0.jpg', true, '2025-12-25 12:23:21.42008');
INSERT INTO public.place_images VALUES (234, 83, '/static/uploads/places/place_83_1.jpg', false, '2025-12-25 12:23:21.42008');
INSERT INTO public.place_images VALUES (235, 83, '/static/uploads/places/place_83_2.jpg', false, '2025-12-25 12:23:21.42008');
INSERT INTO public.place_images VALUES (236, 84, '/static/uploads/places/place_84_0.jpg', true, '2025-12-25 12:23:23.046891');
INSERT INTO public.place_images VALUES (237, 84, '/static/uploads/places/place_84_1.jpg', false, '2025-12-25 12:23:23.046891');
INSERT INTO public.place_images VALUES (238, 84, '/static/uploads/places/place_84_2.jpg', false, '2025-12-25 12:23:23.046891');
INSERT INTO public.place_images VALUES (239, 85, '/static/uploads/places/place_85_0.jpg', true, '2025-12-25 12:23:26.821536');
INSERT INTO public.place_images VALUES (240, 85, '/static/uploads/places/place_85_1.jpg', false, '2025-12-25 12:23:26.821536');
INSERT INTO public.place_images VALUES (241, 85, '/static/uploads/places/place_85_2.jpg', false, '2025-12-25 12:23:26.821536');
INSERT INTO public.place_images VALUES (242, 86, '/static/uploads/places/place_86_0.jpeg', true, '2025-12-25 12:23:28.855829');
INSERT INTO public.place_images VALUES (243, 86, '/static/uploads/places/place_86_1.jpg', false, '2025-12-25 12:23:28.855829');
INSERT INTO public.place_images VALUES (244, 86, '/static/uploads/places/place_86_2.jpg', false, '2025-12-25 12:23:28.855829');
INSERT INTO public.place_images VALUES (245, 87, '/static/uploads/places/place_87_0.jpeg', true, '2025-12-25 12:23:36.490786');
INSERT INTO public.place_images VALUES (246, 87, '/static/uploads/places/place_87_1.jpeg', false, '2025-12-25 12:23:36.490786');
INSERT INTO public.place_images VALUES (247, 87, '/static/uploads/places/place_87_2.jpeg', false, '2025-12-25 12:23:36.490786');
INSERT INTO public.place_images VALUES (248, 88, '/static/uploads/places/place_88_0.jpg', true, '2025-12-25 12:23:42.893374');
INSERT INTO public.place_images VALUES (249, 88, '/static/uploads/places/place_88_1.jpg', false, '2025-12-25 12:23:42.893374');
INSERT INTO public.place_images VALUES (250, 88, '/static/uploads/places/place_88_2.jpeg', false, '2025-12-25 12:23:42.893374');
INSERT INTO public.place_images VALUES (251, 89, '/static/uploads/places/place_89_0.jpg', true, '2025-12-25 12:23:51.142678');
INSERT INTO public.place_images VALUES (252, 89, '/static/uploads/places/place_89_1.jpeg', false, '2025-12-25 12:23:51.142678');
INSERT INTO public.place_images VALUES (253, 89, '/static/uploads/places/place_89_2.jpeg', false, '2025-12-25 12:23:51.142678');
INSERT INTO public.place_images VALUES (254, 90, '/static/uploads/places/place_90_0.jpg', true, '2025-12-25 12:23:54.333195');
INSERT INTO public.place_images VALUES (255, 90, '/static/uploads/places/place_90_1.jpg', false, '2025-12-25 12:23:54.333195');
INSERT INTO public.place_images VALUES (256, 90, '/static/uploads/places/place_90_2.jpg', false, '2025-12-25 12:23:54.333195');
INSERT INTO public.place_images VALUES (257, 91, '/static/uploads/places/place_91_0.jpg', true, '2025-12-25 12:24:00.870555');
INSERT INTO public.place_images VALUES (258, 91, '/static/uploads/places/place_91_1.jpg', false, '2025-12-25 12:24:00.870555');
INSERT INTO public.place_images VALUES (259, 91, '/static/uploads/places/place_91_2.jpg', false, '2025-12-25 12:24:00.870555');
INSERT INTO public.place_images VALUES (260, 92, '/static/uploads/places/place_92_0.jpg', true, '2025-12-25 12:24:04.442953');
INSERT INTO public.place_images VALUES (261, 92, '/static/uploads/places/place_92_1.jpg', false, '2025-12-25 12:24:04.442953');
INSERT INTO public.place_images VALUES (262, 92, '/static/uploads/places/place_92_2.jpg', false, '2025-12-25 12:24:04.442953');
INSERT INTO public.place_images VALUES (263, 93, '/static/uploads/places/place_93_0.jpeg', true, '2025-12-25 12:24:07.638753');
INSERT INTO public.place_images VALUES (264, 93, '/static/uploads/places/place_93_1.jpeg', false, '2025-12-25 12:24:07.638753');
INSERT INTO public.place_images VALUES (265, 93, '/static/uploads/places/place_93_2.jpeg', false, '2025-12-25 12:24:07.638753');
INSERT INTO public.place_images VALUES (266, 94, '/static/uploads/places/place_94_0.jpg', true, '2025-12-25 12:24:11.399595');
INSERT INTO public.place_images VALUES (267, 94, '/static/uploads/places/place_94_1.jpg', false, '2025-12-25 12:24:11.399595');
INSERT INTO public.place_images VALUES (268, 94, '/static/uploads/places/place_94_2.jpg', false, '2025-12-25 12:24:11.399595');
INSERT INTO public.place_images VALUES (269, 95, '/static/uploads/places/place_95_0.jpeg', true, '2025-12-25 12:24:16.774043');
INSERT INTO public.place_images VALUES (270, 95, '/static/uploads/places/place_95_1.jpeg', false, '2025-12-25 12:24:16.774043');
INSERT INTO public.place_images VALUES (271, 95, '/static/uploads/places/place_95_2.jpeg', false, '2025-12-25 12:24:16.774043');
INSERT INTO public.place_images VALUES (272, 96, '/static/uploads/places/place_96_0.jpg', true, '2025-12-25 12:24:20.133979');
INSERT INTO public.place_images VALUES (273, 96, '/static/uploads/places/place_96_1.jpg', false, '2025-12-25 12:24:20.133979');
INSERT INTO public.place_images VALUES (274, 96, '/static/uploads/places/place_96_2.jpg', false, '2025-12-25 12:24:20.133979');
INSERT INTO public.place_images VALUES (275, 97, '/static/uploads/places/place_97_0.jpg', true, '2025-12-25 12:24:23.217517');
INSERT INTO public.place_images VALUES (276, 97, '/static/uploads/places/place_97_1.jpg', false, '2025-12-25 12:24:23.217517');
INSERT INTO public.place_images VALUES (277, 97, '/static/uploads/places/place_97_2.jpg', false, '2025-12-25 12:24:23.217517');
INSERT INTO public.place_images VALUES (278, 98, '/static/uploads/places/place_98_0.jpg', true, '2025-12-25 12:24:25.952052');
INSERT INTO public.place_images VALUES (279, 98, '/static/uploads/places/place_98_1.jpg', false, '2025-12-25 12:24:25.952052');
INSERT INTO public.place_images VALUES (280, 98, '/static/uploads/places/place_98_2.jpg', false, '2025-12-25 12:24:25.952052');
INSERT INTO public.place_images VALUES (281, 99, '/static/uploads/places/place_99_0.jpg', true, '2025-12-25 12:24:28.269331');
INSERT INTO public.place_images VALUES (282, 99, '/static/uploads/places/place_99_1.jpg', false, '2025-12-25 12:24:28.269331');
INSERT INTO public.place_images VALUES (283, 99, '/static/uploads/places/place_99_2.jpg', false, '2025-12-25 12:24:28.269331');
INSERT INTO public.place_images VALUES (284, 100, '/static/uploads/places/place_100_0.jpeg', true, '2025-12-25 12:24:32.307566');
INSERT INTO public.place_images VALUES (285, 100, '/static/uploads/places/place_100_1.jpg', false, '2025-12-25 12:24:32.307566');
INSERT INTO public.place_images VALUES (286, 100, '/static/uploads/places/place_100_2.jpg', false, '2025-12-25 12:24:32.307566');
INSERT INTO public.place_images VALUES (287, 101, '/static/uploads/places/place_101_0.jpeg', true, '2025-12-25 12:24:36.812809');
INSERT INTO public.place_images VALUES (288, 101, '/static/uploads/places/place_101_1.jpeg', false, '2025-12-25 12:24:36.812809');
INSERT INTO public.place_images VALUES (289, 101, '/static/uploads/places/place_101_2.jpeg', false, '2025-12-25 12:24:36.812809');
INSERT INTO public.place_images VALUES (290, 102, '/static/uploads/places/place_102_0.jpg', true, '2025-12-25 12:24:42.393843');
INSERT INTO public.place_images VALUES (291, 102, '/static/uploads/places/place_102_1.jpg', false, '2025-12-25 12:24:42.393843');
INSERT INTO public.place_images VALUES (292, 102, '/static/uploads/places/place_102_2.jpg', false, '2025-12-25 12:24:42.393843');
INSERT INTO public.place_images VALUES (293, 103, '/static/uploads/places/place_103_0.jpg', true, '2025-12-25 12:24:49.130239');
INSERT INTO public.place_images VALUES (294, 103, '/static/uploads/places/place_103_1.jpg', false, '2025-12-25 12:24:49.130239');
INSERT INTO public.place_images VALUES (295, 103, '/static/uploads/places/place_103_2.jpg', false, '2025-12-25 12:24:49.130239');
INSERT INTO public.place_images VALUES (296, 104, '/static/uploads/places/place_104_0.jpg', true, '2025-12-25 12:24:51.837992');
INSERT INTO public.place_images VALUES (297, 104, '/static/uploads/places/place_104_1.jpg', false, '2025-12-25 12:24:51.837992');
INSERT INTO public.place_images VALUES (298, 104, '/static/uploads/places/place_104_2.jpg', false, '2025-12-25 12:24:51.837992');
INSERT INTO public.place_images VALUES (299, 105, '/static/uploads/places/place_105_0.jpg', true, '2025-12-25 12:24:54.408745');
INSERT INTO public.place_images VALUES (300, 105, '/static/uploads/places/place_105_1.jpg', false, '2025-12-25 12:24:54.408745');
INSERT INTO public.place_images VALUES (301, 105, '/static/uploads/places/place_105_2.jpg', false, '2025-12-25 12:24:54.408745');
INSERT INTO public.place_images VALUES (302, 106, '/static/uploads/places/place_106_0.jpeg', true, '2025-12-25 12:25:00.393327');
INSERT INTO public.place_images VALUES (303, 106, '/static/uploads/places/place_106_1.jpeg', false, '2025-12-25 12:25:00.393327');
INSERT INTO public.place_images VALUES (304, 106, '/static/uploads/places/place_106_2.jpeg', false, '2025-12-25 12:25:00.393327');
INSERT INTO public.place_images VALUES (305, 107, '/static/uploads/places/place_107_0.png', true, '2025-12-25 12:25:04.961582');
INSERT INTO public.place_images VALUES (306, 107, '/static/uploads/places/place_107_1.jpeg', false, '2025-12-25 12:25:04.961582');
INSERT INTO public.place_images VALUES (307, 107, '/static/uploads/places/place_107_2.png', false, '2025-12-25 12:25:04.961582');
INSERT INTO public.place_images VALUES (308, 108, '/static/uploads/places/place_108_0.jpg', true, '2025-12-25 12:25:06.371484');
INSERT INTO public.place_images VALUES (309, 108, '/static/uploads/places/place_108_1.jpg', false, '2025-12-25 12:25:06.371484');
INSERT INTO public.place_images VALUES (310, 108, '/static/uploads/places/place_108_2.jpg', false, '2025-12-25 12:25:06.371484');
INSERT INTO public.place_images VALUES (311, 109, '/static/uploads/places/place_109_0.jpeg', true, '2025-12-25 12:25:10.159035');
INSERT INTO public.place_images VALUES (312, 109, '/static/uploads/places/place_109_1.jpeg', false, '2025-12-25 12:25:10.159035');
INSERT INTO public.place_images VALUES (313, 109, '/static/uploads/places/place_109_2.jpg', false, '2025-12-25 12:25:10.159035');
INSERT INTO public.place_images VALUES (314, 110, '/static/uploads/places/place_110_0.jpg', true, '2025-12-25 12:25:17.633537');
INSERT INTO public.place_images VALUES (315, 110, '/static/uploads/places/place_110_1.jpg', false, '2025-12-25 12:25:17.633537');
INSERT INTO public.place_images VALUES (316, 110, '/static/uploads/places/place_110_2.jpg', false, '2025-12-25 12:25:17.633537');
INSERT INTO public.place_images VALUES (317, 111, '/static/uploads/places/place_111_0.jpg', true, '2025-12-25 12:25:24.644021');
INSERT INTO public.place_images VALUES (318, 111, '/static/uploads/places/place_111_1.jpg', false, '2025-12-25 12:25:24.644021');
INSERT INTO public.place_images VALUES (319, 111, '/static/uploads/places/place_111_2.jpg', false, '2025-12-25 12:25:24.644021');
INSERT INTO public.place_images VALUES (320, 112, '/static/uploads/places/place_112_0.jpeg', true, '2025-12-25 12:25:32.345232');
INSERT INTO public.place_images VALUES (321, 112, '/static/uploads/places/place_112_1.jpeg', false, '2025-12-25 12:25:32.345232');
INSERT INTO public.place_images VALUES (322, 112, '/static/uploads/places/place_112_2.jpeg', false, '2025-12-25 12:25:32.345232');
INSERT INTO public.place_images VALUES (323, 113, '/static/uploads/places/place_113_0.jpg', true, '2025-12-25 12:25:41.515406');
INSERT INTO public.place_images VALUES (324, 113, '/static/uploads/places/place_113_1.jpg', false, '2025-12-25 12:25:41.515406');
INSERT INTO public.place_images VALUES (325, 113, '/static/uploads/places/place_113_2.jpg', false, '2025-12-25 12:25:41.515406');
INSERT INTO public.place_images VALUES (326, 114, '/static/uploads/places/place_114_0.jpg', true, '2025-12-25 12:25:46.143588');
INSERT INTO public.place_images VALUES (327, 114, '/static/uploads/places/place_114_1.jpg', false, '2025-12-25 12:25:46.143588');
INSERT INTO public.place_images VALUES (328, 114, '/static/uploads/places/place_114_2.jpg', false, '2025-12-25 12:25:46.143588');
INSERT INTO public.place_images VALUES (329, 115, '/static/uploads/places/place_115_0.jpg', true, '2025-12-25 12:25:49.830786');
INSERT INTO public.place_images VALUES (330, 115, '/static/uploads/places/place_115_1.jpg', false, '2025-12-25 12:25:49.830786');
INSERT INTO public.place_images VALUES (331, 115, '/static/uploads/places/place_115_2.jpg', false, '2025-12-25 12:25:49.830786');
INSERT INTO public.place_images VALUES (332, 116, '/static/uploads/places/place_116_0.jpeg', true, '2025-12-25 12:25:55.792417');
INSERT INTO public.place_images VALUES (333, 116, '/static/uploads/places/place_116_1.jpeg', false, '2025-12-25 12:25:55.792417');
INSERT INTO public.place_images VALUES (334, 116, '/static/uploads/places/place_116_2.jpeg', false, '2025-12-25 12:25:55.792417');
INSERT INTO public.place_images VALUES (335, 117, '/static/uploads/places/place_117_0.jpg', true, '2025-12-25 12:26:07.459303');
INSERT INTO public.place_images VALUES (336, 117, '/static/uploads/places/place_117_1.jpg', false, '2025-12-25 12:26:07.459303');
INSERT INTO public.place_images VALUES (337, 117, '/static/uploads/places/place_117_2.jpg', false, '2025-12-25 12:26:07.459303');
INSERT INTO public.place_images VALUES (338, 118, '/static/uploads/places/place_118_0.jpeg', true, '2025-12-25 12:26:11.860276');
INSERT INTO public.place_images VALUES (339, 118, '/static/uploads/places/place_118_1.jpeg', false, '2025-12-25 12:26:11.860276');
INSERT INTO public.place_images VALUES (340, 118, '/static/uploads/places/place_118_2.jpg', false, '2025-12-25 12:26:11.860276');
INSERT INTO public.place_images VALUES (341, 119, '/static/uploads/places/place_119_0.jpg', true, '2025-12-25 12:26:13.403978');
INSERT INTO public.place_images VALUES (342, 119, '/static/uploads/places/place_119_1.jpg', false, '2025-12-25 12:26:13.403978');
INSERT INTO public.place_images VALUES (343, 119, '/static/uploads/places/place_119_2.jpg', false, '2025-12-25 12:26:13.403978');
INSERT INTO public.place_images VALUES (344, 120, '/static/uploads/places/place_120_0.jpeg', true, '2025-12-25 12:26:18.823474');
INSERT INTO public.place_images VALUES (345, 120, '/static/uploads/places/place_120_1.jpeg', false, '2025-12-25 12:26:18.823474');
INSERT INTO public.place_images VALUES (346, 120, '/static/uploads/places/place_120_2.jpeg', false, '2025-12-25 12:26:18.823474');
INSERT INTO public.place_images VALUES (347, 121, '/static/uploads/places/place_121_0.jpg', true, '2025-12-25 12:26:23.15411');
INSERT INTO public.place_images VALUES (348, 121, '/static/uploads/places/place_121_1.jpg', false, '2025-12-25 12:26:23.15411');
INSERT INTO public.place_images VALUES (349, 121, '/static/uploads/places/place_121_2.jpg', false, '2025-12-25 12:26:23.15411');
INSERT INTO public.place_images VALUES (350, 122, '/static/uploads/places/place_122_0.jpeg', true, '2025-12-25 12:26:26.119837');
INSERT INTO public.place_images VALUES (351, 122, '/static/uploads/places/place_122_1.jpeg', false, '2025-12-25 12:26:26.119837');
INSERT INTO public.place_images VALUES (352, 122, '/static/uploads/places/place_122_2.jpeg', false, '2025-12-25 12:26:26.119837');
INSERT INTO public.place_images VALUES (353, 123, '/static/uploads/places/place_123_0.jpeg', true, '2025-12-25 12:26:28.226841');
INSERT INTO public.place_images VALUES (354, 123, '/static/uploads/places/place_123_1.jpeg', false, '2025-12-25 12:26:28.226841');
INSERT INTO public.place_images VALUES (355, 123, '/static/uploads/places/place_123_2.jpeg', false, '2025-12-25 12:26:28.226841');
INSERT INTO public.place_images VALUES (356, 124, '/static/uploads/places/place_124_0.jpg', true, '2025-12-25 12:26:30.370732');
INSERT INTO public.place_images VALUES (357, 124, '/static/uploads/places/place_124_1.jpg', false, '2025-12-25 12:26:30.370732');
INSERT INTO public.place_images VALUES (358, 124, '/static/uploads/places/place_124_2.jpg', false, '2025-12-25 12:26:30.370732');
INSERT INTO public.place_images VALUES (359, 125, '/static/uploads/places/place_125_0.jpg', true, '2025-12-25 12:26:32.804935');
INSERT INTO public.place_images VALUES (360, 125, '/static/uploads/places/place_125_1.jpg', false, '2025-12-25 12:26:32.804935');
INSERT INTO public.place_images VALUES (361, 125, '/static/uploads/places/place_125_2.jpg', false, '2025-12-25 12:26:32.804935');
INSERT INTO public.place_images VALUES (362, 126, '/static/uploads/places/place_126_0.jpg', true, '2025-12-25 12:26:34.184692');
INSERT INTO public.place_images VALUES (363, 126, '/static/uploads/places/place_126_1.jpg', false, '2025-12-25 12:26:34.184692');
INSERT INTO public.place_images VALUES (364, 126, '/static/uploads/places/place_126_2.jpg', false, '2025-12-25 12:26:34.184692');
INSERT INTO public.place_images VALUES (365, 127, '/static/uploads/places/place_127_0.jpg', true, '2025-12-25 12:26:35.051928');
INSERT INTO public.place_images VALUES (366, 127, '/static/uploads/places/place_127_1.jpg', false, '2025-12-25 12:26:35.051928');
INSERT INTO public.place_images VALUES (367, 127, '/static/uploads/places/place_127_2.jpg', false, '2025-12-25 12:26:35.051928');
INSERT INTO public.place_images VALUES (368, 128, '/static/uploads/places/place_128_0.jpg', true, '2025-12-25 12:26:45.16966');
INSERT INTO public.place_images VALUES (369, 128, '/static/uploads/places/place_128_1.jpg', false, '2025-12-25 12:26:45.16966');
INSERT INTO public.place_images VALUES (370, 128, '/static/uploads/places/place_128_2.jpg', false, '2025-12-25 12:26:45.16966');
INSERT INTO public.place_images VALUES (371, 129, '/static/uploads/places/place_129_0.jpeg', true, '2025-12-25 12:26:48.654554');
INSERT INTO public.place_images VALUES (372, 129, '/static/uploads/places/place_129_1.jpeg', false, '2025-12-25 12:26:48.654554');
INSERT INTO public.place_images VALUES (373, 129, '/static/uploads/places/place_129_2.jpg', false, '2025-12-25 12:26:48.654554');
INSERT INTO public.place_images VALUES (374, 130, '/static/uploads/places/place_130_0.jpeg', true, '2025-12-25 12:26:52.371928');
INSERT INTO public.place_images VALUES (375, 130, '/static/uploads/places/place_130_1.jpeg', false, '2025-12-25 12:26:52.371928');
INSERT INTO public.place_images VALUES (376, 130, '/static/uploads/places/place_130_2.jpg', false, '2025-12-25 12:26:52.371928');


--
-- TOC entry 5083 (class 0 OID 39178)
-- Dependencies: 229
-- Data for Name: place_types; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.place_types VALUES (1, 'Du lịch');
INSERT INTO public.place_types VALUES (2, 'Ẩm thực');
INSERT INTO public.place_types VALUES (3, 'Lưu trú');


--
-- TOC entry 5085 (class 0 OID 39187)
-- Dependencies: 231
-- Data for Name: places; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.places VALUES (1, 1, 1, 'Hồ Hoàn Kiếm', 'Trái tim thủ đô, biểu tượng văn hóa và lịch sử.', 'Hoàn Kiếm, Hà Nội', 20.976208, 105.801471, 4.60, 1369, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (2, 1, 1, 'Đền Ngọc Sơn', 'Đền thờ nằm trên đảo ngọc giữa hồ Hoàn Kiếm.', 'Hoàn Kiếm, Hà Nội', 20.999066, 105.868568, 4.30, 1077, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (3, 1, 1, 'Nhà hát Lớn Hà Nội', 'Kiệt tác kiến trúc Pháp, nơi biểu diễn nghệ thuật hàn lâm.', 'Hoàn Kiếm, Hà Nội', 20.989322, 105.896009, 4.50, 895, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (4, 1, 1, 'Nhà thờ Lớn Hà Nội', 'Nhà thờ phong cách Gothic cổ kính, điểm check-in nổi tiếng.', 'Hoàn Kiếm, Hà Nội', 20.978883, 105.901107, 4.60, 416, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (5, 1, 5, 'Văn Miếu - Quốc Tử Giám', 'Trường đại học đầu tiên của Việt Nam, biểu tượng hiếu học.', 'Đống Đa, Hà Nội', 20.978566, 105.846418, 4.20, 1778, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (6, 1, 2, 'Hoàng thành Thăng Long', 'Quần thể di tích gắn liền với lịch sử kinh thành Thăng Long.', 'Ba Đình, Hà Nội', 20.985954, 105.839141, 4.20, 1900, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (7, 1, 2, 'Lăng Chủ tịch Hồ Chí Minh', 'Nơi an nghỉ của chủ tịch Hồ Chí Minh.', 'Ba Đình, Hà Nội', 21.000413, 105.805911, 4.70, 1752, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (8, 1, 2, 'Chùa Một Cột', 'Ngôi chùa có kiến trúc độc đáo hình bông sen.', 'Ba Đình, Hà Nội', 21.019108, 105.897758, 4.00, 742, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (9, 1, 6, 'Bảo tàng Dân tộc học', 'Trưng bày văn hóa 54 dân tộc, không gian văn hóa ngoài trời.', 'Cầu Giấy, Hà Nội', 20.973900, 105.833431, 4.80, 721, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (10, 1, 1, 'Nhà tù Hỏa Lò', 'Minh chứng lịch sử hào hùng và bi tráng thời chiến.', 'Hoàn Kiếm, Hà Nội', 21.040577, 105.848720, 4.40, 1572, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (11, 1, 3, 'Hồ Tây', 'Hồ nước ngọt lớn nhất nội thành, không gian thoáng đãng.', 'Tây Hồ, Hà Nội', 20.993163, 105.828962, 4.00, 1854, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (12, 1, 3, 'Chùa Trấn Quốc', 'Ngôi chùa cổ nhất Hà Nội (hơn 1500 năm) nằm ven Hồ Tây.', 'Tây Hồ, Hà Nội', 21.043214, 105.823197, 4.40, 1161, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (13, 1, 3, 'Phủ Tây Hồ', 'Nơi thờ Chúa Liễu Hạnh, nổi tiếng linh thiêng.', 'Tây Hồ, Hà Nội', 20.981210, 105.865868, 4.90, 1672, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (14, 1, 9, 'Cầu Long Biên', '"Chứng nhân lịch sử" vắt qua sông Hồng, kiến trúc Pháp.', 'Long Biên, Hà Nội', 21.014380, 105.890226, 4.10, 670, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (15, 1, 1, 'Chợ Đồng Xuân', 'Chợ đầu mối lớn nhất khu phố cổ, buôn bán sầm uất.', 'Hoàn Kiếm, Hà Nội', 21.014663, 105.843146, 5.00, 839, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (16, 1, 1, 'Phố cổ Hà Nội', '36 phố phường với nghề thủ công truyền thống.', 'Hoàn Kiếm, Hà Nội', 20.990708, 105.835347, 4.80, 1694, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (17, 1, 1, 'Bảo tàng Lịch sử Quốc gia', 'Lưu giữ hiện vật lịch sử từ thời tiền sử đến nay.', 'Hoàn Kiếm, Hà Nội', 21.003952, 105.821323, 4.30, 197, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (18, 1, 1, 'Bảo tàng Phụ nữ Việt Nam', 'Tôn vinh vai trò và vẻ đẹp của phụ nữ Việt.', 'Hoàn Kiếm, Hà Nội', 21.006989, 105.872990, 4.40, 1982, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (19, 1, 2, 'Bảo tàng Mỹ thuật Việt Nam', 'Nơi lưu giữ các tác phẩm hội họa, điêu khắc giá trị.', 'Ba Đình, Hà Nội', 20.983209, 105.821428, 4.70, 1650, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (20, 1, 2, 'Cột cờ Hà Nội', 'Biểu tượng quân sự, nằm trong khuôn viên bảo tàng Lịch sử QS.', 'Ba Đình, Hà Nội', 21.021545, 105.895958, 4.00, 1710, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (21, 1, 2, 'Đền Quán Thánh', 'Một trong "Thăng Long tứ trấn", thờ Huyền Thiên Trấn Vũ.', 'Ba Đình, Hà Nội', 21.030525, 105.832849, 4.30, 1004, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (22, 1, 1, 'Con đường Gốm sứ', 'Bức tranh tường gốm sứ dài nhất thế giới.', 'Hoàn Kiếm/Tây Hồ, Hà Nội', 21.018480, 105.841907, 4.10, 1120, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (23, 1, 14, 'Làng gốm Bát Tràng', 'Làng nghề gốm sứ truyền thống 700 năm tuổi.', 'Gia Lâm, Hà Nội', 20.983426, 105.801363, 4.60, 1373, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (24, 1, 12, 'Làng lụa Vạn Phúc', 'Làng dệt lụa tơ tằm nổi tiếng và lâu đời.', 'Hà Đông, Hà Nội', 20.985297, 105.798952, 4.90, 535, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (25, 1, 13, 'Làng cổ Đường Lâm', 'Làng cổ đá ong, quê hương của hai vị vua.', 'Sơn Tây, Hà Nội', 21.022211, 105.880195, 4.50, 1562, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (26, 1, 1, 'Vườn quốc gia Ba Vì', 'Núi non hùng vĩ, khí hậu mát mẻ, có đền thờ Bác Hồ.', 'Ba Vì, Hà Nội', 20.997605, 105.800413, 4.30, 1882, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (27, 1, 14, 'Thành Cổ Loa', 'Kinh đô của nhà nước Âu Lạc thời An Dương Vương.', 'Đông Anh, Hà Nội', 20.988281, 105.892691, 4.30, 774, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (28, 1, 15, 'Chùa Hương', 'Quần thể văn hóa - tôn giáo lớn, nổi tiếng với lễ hội xuân.', 'Mỹ Đức, Hà Nội', 21.083573, 105.827280, 4.40, 217, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (29, 1, 12, 'Chùa Thầy', 'Gắn liền với thiền sư Từ Đạo Hạnh, phong cảnh hữu tình.', 'Quốc Oai, Hà Nội', 21.054561, 105.837461, 4.60, 348, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (30, 1, 12, 'Chùa Tây Phương', 'Nổi tiếng với bộ tượng La Hán điêu khắc tinh xảo.', 'Thạch Thất, Hà Nội', 21.004807, 105.891031, 4.70, 391, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (31, 1, 10, 'Thiên đường Bảo Sơn', 'Tổ hợp vui chơi, giải trí, thủy cung, làng nghề.', 'Hoài Đức, Hà Nội', 20.992431, 105.850742, 4.30, 1600, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (32, 1, 2, 'Lotte Observation Deck', 'Đài quan sát kính trên tầng 65 tòa nhà Lotte.', 'Ba Đình, Hà Nội', 21.070165, 105.812337, 4.00, 1062, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (33, 1, 4, 'Thủy cung Vinpearl Aquarium', 'Thủy cung lớn trong lòng đất tại Times City.', 'Hai Bà Trưng, Hà Nội', 21.047130, 105.899417, 4.70, 1112, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (34, 1, 1, 'Phố đi bộ Hồ Gươm', 'Không gian văn hóa cộng đồng cuối tuần (T6-CN).', 'Hoàn Kiếm, Hà Nội', 21.082801, 105.791330, 4.10, 485, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (35, 1, 1, 'Ô Quan Chưởng', 'Cửa ô duy nhất còn lại của kinh thành Thăng Long xưa.', 'Hoàn Kiếm, Hà Nội', 21.068136, 105.881007, 4.10, 1693, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (36, 1, 7, 'Bảo tàng Phòng không - KQ', 'Trưng bày máy bay, khí tài quân sự và xác B52.', 'Thanh Xuân, Hà Nội', 21.006534, 105.887641, 4.20, 961, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (37, 1, 4, 'Công viên Thống Nhất', '"Lá phổi xanh" lớn của thủ đô, hồ Bảy Mẫu.', 'Hai Bà Trưng, Hà Nội', 20.968074, 105.835671, 4.70, 219, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (38, 1, 8, 'Công viên Yên Sở', 'Công viên xanh rộng lớn, thích hợp cắm trại, dã ngoại.', 'Hoàng Mai, Hà Nội', 21.082611, 105.850285, 4.80, 635, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (39, 1, 2, 'Đền Voi Phục', 'Một trong Thăng Long tứ trấn, thờ hoàng tử Linh Lang.', 'Ba Đình, Hà Nội', 21.029672, 105.893855, 4.60, 487, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (40, 1, 5, 'Đền Kim Liên', 'Một trong Thăng Long tứ trấn, trấn giữ phía Nam.', 'Đống Đa, Hà Nội', 21.051700, 105.832664, 4.20, 1674, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (41, 1, 1, 'Đền Bạch Mã', 'Trấn giữ phía Đông kinh thành, nằm trong phố cổ.', 'Hoàn Kiếm, Hà Nội', 21.018598, 105.802406, 4.40, 396, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (42, 1, 12, 'Núi Trầm', '"Cao nguyên đá" thu nhỏ, địa điểm trekking nhẹ nhàng.', 'Chương Mỹ, Hà Nội', 20.997351, 105.886671, 4.70, 1006, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (43, 1, 15, 'Hồ Quan Sơn', 'Được ví như "Hạ Long trên cạn" của Hà Nội.', 'Mỹ Đức, Hà Nội', 21.043977, 105.792753, 4.20, 1271, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (44, 1, 13, 'Làng văn hóa các DTVN', 'Mô hình tái hiện văn hóa 54 dân tộc Việt Nam.', 'Sơn Tây, Hà Nội', 20.986076, 105.896383, 4.80, 1140, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (45, 1, 10, 'Bảo tàng Hà Nội', 'Kiến trúc kim tự tháp ngược, trưng bày lịch sử thủ đô.', 'Nam Từ Liêm, Hà Nội', 20.975577, 105.829026, 4.80, 602, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (46, 1, 1, 'Phố bích họa Phùng Hưng', 'Đoạn đường vòm cầu xe lửa với các bức tranh bích họa.', 'Hoàn Kiếm, Hà Nội', 21.007600, 105.852860, 4.70, 1031, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (47, 1, 3, 'Cầu Nhật Tân', 'Cầu dây văng hiện đại, đẹp lung linh về đêm.', 'Tây Hồ, Hà Nội', 21.027359, 105.843198, 4.90, 173, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (48, 1, 3, 'Bãi đá Sông Hồng', 'Vườn hoa, điểm chụp ảnh và cắm trại ven sông.', 'Tây Hồ, Hà Nội', 21.043808, 105.842794, 5.00, 834, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (49, 1, 16, 'Việt Phủ Thành Chương', 'Bảo tàng tư nhân đậm chất văn hóa Bắc Bộ xưa.', 'Sóc Sơn, Hà Nội', 20.991562, 105.871222, 4.30, 1109, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (50, 1, 1, 'Nhà hát Múa rối Thăng Long', 'Biểu diễn múa rối nước cổ truyền độc đáo.', 'Hoàn Kiếm, Hà Nội', 20.982326, 105.818558, 4.20, 1719, 0.00, '08:00:00', '17:00:00', 0.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (51, 2, 4, 'Phở Thìn Lò Đúc', 'Phở bò tái lăn trứ danh, nhiều hành, nước béo.', 'Hai Bà Trưng, Hà Nội', 21.026245, 105.903640, 4.50, 648, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (52, 2, 1, 'Chả cá Lã Vọng', 'Món ăn đặc sản "huyền thoại" của Hà Nội.', 'Hoàn Kiếm, Hà Nội', 21.085155, 105.870321, 3.90, 181, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (53, 2, 4, 'Bún chả Hương Liên', 'Quán "Bún chả Obama", nổi tiếng thế giới.', 'Hai Bà Trưng, Hà Nội', 21.022086, 105.872854, 4.70, 683, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (54, 2, 1, 'Bánh mì 25', 'Bánh mì đắt khách du lịch, nhân đầy đặn.', 'Hoàn Kiếm, Hà Nội', 21.005009, 105.909615, 4.10, 405, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (55, 2, 1, 'Pizza 4P''s Tràng Tiền', 'Pizza lò củi kết hợp phong cách Nhật - Ý - Việt.', 'Hoàn Kiếm, Hà Nội', 21.080906, 105.828404, 3.90, 724, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (56, 2, 1, 'Nhà hàng Ngon', 'Tập hợp các món ăn đường phố trong biệt thự Pháp.', 'Hoàn Kiếm, Hà Nội', 21.070506, 105.834312, 4.20, 55, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (57, 2, 5, 'Tầm Vị', 'Cơm nhà Bắc Bộ chuẩn vị, đạt sao Michelin.', 'Đống Đa, Hà Nội', 20.975128, 105.871338, 4.10, 406, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (58, 2, 1, 'Xôi Yến', 'Món xôi xéo, xôi ngô nổi tiếng phố Nguyễn Hữu Huân.', 'Hoàn Kiếm, Hà Nội', 21.075744, 105.799304, 3.80, 418, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (59, 2, 1, 'Cafe Giảng', 'Nơi khai sinh ra món Cà phê trứng lừng danh.', 'Hoàn Kiếm, Hà Nội', 21.074741, 105.876111, 4.00, 466, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (60, 2, 1, 'Cafe Đinh', 'Cafe trứng view hồ Gươm, không gian hoài cổ.', 'Hoàn Kiếm, Hà Nội', 21.077930, 105.898563, 4.20, 303, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (61, 2, 1, 'The Note Coffee', 'Quán cafe độc đáo dán kín giấy nhớ của khách.', 'Hoàn Kiếm, Hà Nội', 21.028609, 105.898553, 3.50, 596, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (62, 2, 1, 'Loading T Cafe', 'Cafe trong biệt thự cổ, không gian yên tĩnh.', 'Hoàn Kiếm, Hà Nội', 21.010078, 105.813714, 4.10, 554, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (63, 2, 1, 'Maison Vie', 'Ẩm thực Pháp tinh tế trong không gian sang trọng.', 'Hoàn Kiếm, Hà Nội', 21.062041, 105.807787, 4.70, 618, 0.00, '09:00:00', '22:00:00', 240000.00, 360000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (64, 2, 1, 'La Verticale', 'Fusion Pháp - Việt do đầu bếp Didier Corlou sáng tạo.', 'Hoàn Kiếm, Hà Nội', 21.029666, 105.820358, 4.60, 271, 0.00, '09:00:00', '22:00:00', 480000.00, 720000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (65, 2, 1, 'Press Club Hanoi', 'Ẩm thực Âu đẳng cấp, view đẹp cạnh Nhà hát Lớn.', 'Hoàn Kiếm, Hà Nội', 21.028428, 105.868979, 3.90, 645, 0.00, '09:00:00', '22:00:00', 480000.00, 720000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (66, 2, 1, 'Bún thang Bà Đức', 'Bún thang Cầu Gỗ thanh tao, chuẩn vị Hà thành.', 'Hoàn Kiếm, Hà Nội', 20.978158, 105.880423, 4.10, 56, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (67, 2, 1, 'Phở 10 Lý Quốc Sư', 'Thương hiệu phở bò nổi tiếng, nước dùng trong ngọt.', 'Hoàn Kiếm, Hà Nội', 21.074488, 105.885755, 3.80, 740, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (68, 2, 4, 'Bánh cuốn Bà Hoành', 'Bánh cuốn Thanh Trì mỏng tang, chả quế ngon.', 'Hai Bà Trưng, Hà Nội', 21.055501, 105.871444, 4.70, 452, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (69, 2, 11, 'Lẩu Cua Đồng Song Hà', 'Chuyên lẩu cua đồng và món ăn đồng quê.', 'Bắc Từ Liêm, Hà Nội', 21.053674, 105.872737, 3.90, 641, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (70, 2, 3, 'Sen Tây Hồ', 'Buffet quốc tế lớn nhất Hà Nội, đa dạng món.', 'Tây Hồ, Hà Nội', 21.080603, 105.904767, 3.70, 162, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (71, 2, 2, 'Grill 63 (Lotte)', 'Bít tết bò Wagyu thượng hạng, view tầng 63.', 'Ba Đình, Hà Nội', 21.030681, 105.879378, 4.20, 325, 0.00, '09:00:00', '22:00:00', 480000.00, 720000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (72, 2, 1, 'Ưu Đàm Chay', 'Ẩm thực chay cao cấp, không gian thiền tịnh.', 'Hoàn Kiếm, Hà Nội', 21.027649, 105.895835, 4.50, 412, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (73, 2, 7, 'Trill Rooftop Cafe', 'Cafe sân thượng có hồ bơi, view thoáng rộng.', 'Thanh Xuân, Hà Nội', 21.083505, 105.832269, 4.60, 272, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (74, 2, 2, 'Manzi Art Space', 'Không gian nghệ thuật đương đại kết hợp cafe.', 'Ba Đình, Hà Nội', 21.087799, 105.869138, 4.30, 113, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (75, 2, 6, 'Cốm Vòng (Làng Vòng)', 'Đặc sản mùa thu Hà Nội, mua mang về.', 'Cầu Giấy, Hà Nội', 21.040367, 105.887167, 4.20, 338, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (76, 2, 1, 'Kem Tràng Tiền', '"Văn hóa" ăn kem đứng ngay trung tâm thủ đô.', 'Hoàn Kiếm, Hà Nội', 21.011081, 105.848687, 4.10, 538, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (77, 2, 2, 'Home Hanoi Restaurant', 'Món Việt truyền thống trong biệt thự Pháp cổ.', 'Ba Đình, Hà Nội', 21.060094, 105.867811, 4.60, 680, 0.00, '09:00:00', '22:00:00', 240000.00, 360000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (78, 2, 1, 'Sadhu Vegetarian', 'Buffet chay gọi món, kiến trúc ấn tượng.', 'Hoàn Kiếm, Hà Nội', 21.050753, 105.831566, 4.50, 268, 0.00, '09:00:00', '22:00:00', 120000.00, 180000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (79, 2, 1, 'Metropole Tea Club', 'Trà chiều sang trọng trong khách sạn Metropole.', 'Hoàn Kiếm, Hà Nội', 20.978792, 105.841366, 3.50, 600, 0.00, '09:00:00', '22:00:00', 240000.00, 360000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (80, 2, 1, 'Nộm Long Vi Dung', 'Nộm bò khô phố Hồ Hoàn Kiếm nổi tiếng.', 'Hoàn Kiếm, Hà Nội', 21.002423, 105.798842, 4.20, 383, 0.00, '09:00:00', '22:00:00', 40000.00, 60000.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (81, 3, 1, 'Sofitel Legend Metropole', 'Biểu tượng lịch sử, sang trọng bậc nhất từ 1901.', 'Hoàn Kiếm, Hà Nội', 20.983270, 105.905275, 4.80, 333, 0.00, NULL, NULL, 6000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (82, 3, 10, 'JW Marriott Hanoi', 'Kiến trúc "con rồng", nơi ở của các tổng thống Mỹ.', 'Nam Từ Liêm, Hà Nội', 20.988010, 105.885696, 5.00, 294, 0.00, NULL, NULL, 6000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (83, 3, 2, 'Lotte Hotel Hanoi', 'Tầm nhìn toàn cảnh thành phố từ trên cao.', 'Ba Đình, Hà Nội', 20.995853, 105.881651, 4.80, 425, 0.00, NULL, NULL, 6000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (84, 3, 3, 'InterContinental Westlake', 'Khách sạn xây trên mặt nước Hồ Tây, resort phố.', 'Tây Hồ, Hà Nội', 20.993310, 105.852875, 4.10, 349, 0.00, NULL, NULL, 6000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (85, 3, 1, 'Capella Hanoi', 'Thiết kế bởi Bill Bensley, phong cách Opera 1920s.', 'Hoàn Kiếm, Hà Nội', 21.038403, 105.818968, 4.30, 443, 0.00, NULL, NULL, 6000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (86, 3, 1, 'Apricot Hotel', 'View trực diện Hồ Gươm, phong cách nghệ thuật.', 'Hoàn Kiếm, Hà Nội', 21.023794, 105.880132, 4.00, 423, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (87, 3, 2, 'Pan Pacific Hanoi', 'View tuyệt đẹp ra Hồ Tây và sông Hồng.', 'Ba Đình, Hà Nội', 21.020560, 105.819625, 4.80, 55, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (88, 3, 3, 'Sheraton Hanoi', 'Không gian xanh mát, yên tĩnh ven hồ.', 'Tây Hồ, Hà Nội', 21.002931, 105.851660, 4.40, 437, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (89, 3, 1, 'Melia Hanoi', 'Vị trí trung tâm, dịch vụ hội nghị chuyên nghiệp.', 'Hoàn Kiếm, Hà Nội', 21.078440, 105.829349, 4.50, 343, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (90, 3, 2, 'Hanoi Daewoo Hotel', 'Khách sạn 5 sao lâu đời, phong cách cổ điển.', 'Ba Đình, Hà Nội', 21.007793, 105.888579, 4.80, 360, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (91, 3, 1, 'La Siesta Premium Hang Be', 'Dịch vụ xuất sắc, Sky bar đẹp trong phố cổ.', 'Hoàn Kiếm, Hà Nội', 21.043839, 105.861098, 4.80, 450, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (92, 3, 1, 'Peridot Grand Luxury', 'Khách sạn mới, sang trọng, bể bơi vô cực.', 'Hoàn Kiếm, Hà Nội', 21.046834, 105.863538, 4.70, 426, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (93, 3, 1, 'The Oriental Jade', 'Gần Nhà thờ Lớn, thiết kế tinh tế.', 'Hoàn Kiếm, Hà Nội', 20.982200, 105.892619, 4.10, 236, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (94, 3, 1, 'Silk Path Boutique', 'View ra hồ Hoàn Kiếm, phong cách ấm cúng.', 'Hoàn Kiếm, Hà Nội', 21.056856, 105.840467, 4.30, 365, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (95, 3, 1, 'Tirant Hotel', 'Nằm giữa phố cổ, có bể bơi ngoài trời.', 'Hoàn Kiếm, Hà Nội', 21.022477, 105.856765, 4.70, 65, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (96, 3, 1, 'Golden Silk Boutique', 'Phong cách Á Đông kết hợp hiện đại.', 'Hoàn Kiếm, Hà Nội', 20.972423, 105.820673, 4.40, 131, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (97, 3, 1, 'Acoustic Hotel & Spa', 'Khu vực khu phố Pháp, thiết kế tân cổ điển.', 'Hoàn Kiếm, Hà Nội', 20.973237, 105.856624, 4.20, 454, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (98, 3, 1, 'Hanoi Pearl Hotel', 'Gần phố đi bộ, tiện nghi hiện đại.', 'Hoàn Kiếm, Hà Nội', 21.065866, 105.879726, 4.00, 148, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (99, 3, 1, 'Essence Hanoi Hotel', 'Dịch vụ khách hàng được đánh giá rất cao.', 'Hoàn Kiếm, Hà Nội', 21.019977, 105.855678, 4.20, 364, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (100, 3, 1, 'O''Gallery Premier', 'Thiết kế sang trọng, màu xanh ngọc bích chủ đạo.', 'Hoàn Kiếm, Hà Nội', 21.076617, 105.835267, 4.40, 333, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (101, 3, 1, 'Solaria Hanoi Hotel', 'Sân thượng view đẹp nhìn ra Nhà thờ và Hồ Gươm.', 'Hoàn Kiếm, Hà Nội', 21.018559, 105.880974, 4.40, 189, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (102, 3, 1, 'MK Premier Boutique', 'Kiến trúc độc đáo, không gian mở.', 'Hoàn Kiếm, Hà Nội', 20.990834, 105.889498, 4.60, 484, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (103, 3, 1, 'Anatole Hotel', 'Nằm trên phố Nhà Chung, hiện đại và tiện lợi.', 'Hoàn Kiếm, Hà Nội', 20.998440, 105.863038, 4.90, 459, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (104, 3, 1, 'Minerva Church Hotel', 'Ngay sát Nhà thờ Lớn, giá cả hợp lý.', 'Hoàn Kiếm, Hà Nội', 21.006137, 105.873235, 4.50, 357, 0.00, NULL, NULL, 500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (105, 3, 1, 'Hanoi La Castela', 'Nhỏ xinh, nằm trong khu phố nhộn nhịp.', 'Hoàn Kiếm, Hà Nội', 21.080932, 105.875050, 4.40, 117, 0.00, NULL, NULL, 500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (106, 3, 10, 'InterContinental Landmark72', 'Khách sạn cao nhất Hà Nội (tòa Keangnam).', 'Nam Từ Liêm, Hà Nội', 21.079496, 105.845795, 4.70, 382, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (107, 3, 10, 'Hyatt Regency West Hanoi', 'Gần sân vận động Mỹ Đình, tiện nghi thương gia.', 'Nam Từ Liêm, Hà Nội', 21.085418, 105.795601, 4.90, 402, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (108, 3, 6, 'Novotel Suites Hanoi', 'Phong cách căn hộ, phù hợp công tác dài ngày.', 'Cầu Giấy, Hà Nội', 21.042311, 105.907845, 5.00, 22, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (109, 3, 5, 'Pullman Hanoi', 'Nổi bật với giếng trời lớn, gần Văn Miếu.', 'Đống Đa, Hà Nội', 21.010479, 105.800734, 4.70, 338, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (110, 3, 4, 'Hotel du Parc', 'Trước là Nikko, dịch vụ chuẩn Nhật Bản.', 'Hai Bà Trưng, Hà Nội', 21.048035, 105.834800, 4.80, 41, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (111, 3, 1, 'Mövenpick Hotel', 'Kiến trúc Pháp cổ, sang trọng và lịch lãm.', 'Hoàn Kiếm, Hà Nội', 21.071093, 105.837611, 4.30, 191, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (112, 3, 1, 'Mercure Hanoi La Gare', 'Nằm cạnh ga Hà Nội, thuận tiện di chuyển.', 'Hoàn Kiếm, Hà Nội', 21.041449, 105.869758, 5.00, 186, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (113, 3, 1, 'Hilton Garden Inn', 'Tiêu chuẩn quốc tế, gần Nhà hát Lớn.', 'Hoàn Kiếm, Hà Nội', 20.984219, 105.792031, 4.40, 37, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (114, 3, 2, 'Fortuna Hotel', 'Trung tâm giải trí, sòng bạc, ẩm thực Trung Hoa.', 'Ba Đình, Hà Nội', 21.036497, 105.878687, 4.50, 499, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (115, 3, 5, 'Grand Mercure Hanoi', 'Thiết kế đậm chất văn hóa Việt Nam đương đại.', 'Đống Đa, Hà Nội', 21.033189, 105.857235, 4.80, 165, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (116, 3, 1, 'Somerset Grand Hanoi', 'Căn hộ dịch vụ cao cấp tại tháp Hà Nội.', 'Hoàn Kiếm, Hà Nội', 21.003649, 105.865815, 4.10, 235, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (117, 3, 3, 'Fraser Suites', 'Căn hộ dịch vụ view Hồ Tây, yên tĩnh.', 'Tây Hồ, Hà Nội', 20.972512, 105.849144, 4.50, 323, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (118, 3, 3, 'Oakwood Residence', 'Căn hộ hiện đại, khu vực người nước ngoài.', 'Tây Hồ, Hà Nội', 21.034899, 105.906924, 4.70, 174, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (119, 3, 3, 'Elegant Suites Westlake', 'Không gian rộng, phù hợp gia đình.', 'Tây Hồ, Hà Nội', 21.042631, 105.878435, 4.20, 31, 0.00, NULL, NULL, 3000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (120, 3, 2, 'Super Hotel Candle', 'Khách sạn phong cách Nhật, có bể tắm khoáng.', 'Ba Đình, Hà Nội', 21.014316, 105.843146, 4.70, 180, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (121, 3, 5, 'Bao Son International', 'Khách sạn lâu đời, có bể bơi 4 mùa.', 'Đống Đa, Hà Nội', 21.076250, 105.798951, 4.70, 413, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (122, 3, 1, 'The Lapis Hotel', 'Gần các đại sứ quán, yên tĩnh và sang trọng.', 'Hoàn Kiếm, Hà Nội', 21.059257, 105.829277, 4.60, 80, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (123, 3, 2, 'Army Hotel (Khách sạn Quân đội)', 'Không gian sân vườn rộng, kiến trúc thuộc địa.', 'Ba Đình, Hà Nội', 21.031727, 105.858340, 4.40, 249, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (124, 3, 1, 'Thang Long Opera Hotel', 'Gần nhà hát lớn, giá cả phải chăng.', 'Hoàn Kiếm, Hà Nội', 21.013123, 105.841444, 4.50, 133, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (125, 3, 2, 'Flower Garden Hotel', 'Gần khu vực phố cổ và hồ Trúc Bạch.', 'Ba Đình, Hà Nội', 21.016224, 105.795165, 4.90, 405, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (126, 3, 6, 'Smarana Hanoi Heritage', 'Thiết kế cảm hứng từ tranh Hàng Trống độc đáo.', 'Cầu Giấy, Hà Nội', 20.970410, 105.808932, 4.90, 157, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (127, 3, 2, 'Grand Vista Hanoi', 'Hiện đại, gần hồ Giảng Võ.', 'Ba Đình, Hà Nội', 21.043344, 105.888769, 4.10, 82, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (128, 3, 2, 'Dolce by Wyndham Hanoi', 'Khách sạn "dát vàng" nổi tiếng.', 'Ba Đình, Hà Nội', 21.015163, 105.893423, 4.90, 297, 0.00, NULL, NULL, 6000000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (129, 3, 1, 'Silk Queen Grand', 'Vị trí trung tâm, tiện nghi đầy đủ.', 'Hoàn Kiếm, Hà Nội', 21.017593, 105.820058, 4.00, 87, 0.00, NULL, NULL, 1500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);
INSERT INTO public.places VALUES (130, 3, 1, 'Babylon Grand Hotel', 'Giá tốt, có spa và nhà hàng view phố.', 'Hoàn Kiếm, Hà Nội', 21.015221, 105.896420, 4.50, 369, 0.00, NULL, NULL, 500000.00, 0.00, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358', NULL);


--
-- TOC entry 5088 (class 0 OID 39232)
-- Dependencies: 234
-- Data for Name: restaurants; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.restaurants VALUES (51, 'Nhà hàng', 50000.00);
INSERT INTO public.restaurants VALUES (52, 'Nhà hàng', 150000.00);
INSERT INTO public.restaurants VALUES (53, 'Nhà hàng', 50000.00);
INSERT INTO public.restaurants VALUES (54, 'Street food', 50000.00);
INSERT INTO public.restaurants VALUES (55, 'Nhà hàng', 150000.00);
INSERT INTO public.restaurants VALUES (56, 'Nhà hàng', 150000.00);
INSERT INTO public.restaurants VALUES (57, 'Nhà hàng', 150000.00);
INSERT INTO public.restaurants VALUES (58, 'Street food', 50000.00);
INSERT INTO public.restaurants VALUES (59, 'Cafe', 50000.00);
INSERT INTO public.restaurants VALUES (60, 'Cafe', 50000.00);
INSERT INTO public.restaurants VALUES (61, 'Cafe', 50000.00);
INSERT INTO public.restaurants VALUES (62, 'Cafe', 50000.00);
INSERT INTO public.restaurants VALUES (63, 'Nhà hàng', 300000.00);
INSERT INTO public.restaurants VALUES (64, 'Nhà hàng', 600000.00);
INSERT INTO public.restaurants VALUES (65, 'Nhà hàng', 600000.00);
INSERT INTO public.restaurants VALUES (66, 'Street food', 50000.00);
INSERT INTO public.restaurants VALUES (67, 'Nhà hàng', 50000.00);
INSERT INTO public.restaurants VALUES (68, 'Street food', 50000.00);
INSERT INTO public.restaurants VALUES (69, 'Nhà hàng', 150000.00);
INSERT INTO public.restaurants VALUES (70, 'Buffet', 150000.00);
INSERT INTO public.restaurants VALUES (71, 'Nhà hàng', 600000.00);
INSERT INTO public.restaurants VALUES (72, 'Nhà hàng', 150000.00);
INSERT INTO public.restaurants VALUES (73, 'Cafe', 150000.00);
INSERT INTO public.restaurants VALUES (74, 'Cafe/Bar', 150000.00);
INSERT INTO public.restaurants VALUES (75, 'Đặc sản', 50000.00);
INSERT INTO public.restaurants VALUES (76, 'Ăn vặt', 50000.00);
INSERT INTO public.restaurants VALUES (77, 'Nhà hàng', 300000.00);
INSERT INTO public.restaurants VALUES (78, 'Nhà hàng', 150000.00);
INSERT INTO public.restaurants VALUES (79, 'Cafe/Trà', 300000.00);
INSERT INTO public.restaurants VALUES (80, 'Street food', 50000.00);


--
-- TOC entry 5073 (class 0 OID 39105)
-- Dependencies: 219
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.roles VALUES (1, 'admin');
INSERT INTO public.roles VALUES (2, 'user');


--
-- TOC entry 5079 (class 0 OID 39150)
-- Dependencies: 225
-- Data for Name: token_refresh; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- TOC entry 5090 (class 0 OID 39254)
-- Dependencies: 236
-- Data for Name: tourist_attractions; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.tourist_attractions VALUES (1, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (2, 30000.00, true);
INSERT INTO public.tourist_attractions VALUES (3, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (4, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (5, 30000.00, true);
INSERT INTO public.tourist_attractions VALUES (6, 30000.00, true);
INSERT INTO public.tourist_attractions VALUES (7, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (8, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (9, 40000.00, true);
INSERT INTO public.tourist_attractions VALUES (10, 30000.00, true);
INSERT INTO public.tourist_attractions VALUES (11, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (12, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (13, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (14, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (15, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (16, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (17, 40000.00, true);
INSERT INTO public.tourist_attractions VALUES (18, 40000.00, true);
INSERT INTO public.tourist_attractions VALUES (19, 40000.00, true);
INSERT INTO public.tourist_attractions VALUES (20, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (21, 10000.00, true);
INSERT INTO public.tourist_attractions VALUES (22, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (23, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (24, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (25, 20000.00, true);
INSERT INTO public.tourist_attractions VALUES (26, 60000.00, true);
INSERT INTO public.tourist_attractions VALUES (27, 10000.00, true);
INSERT INTO public.tourist_attractions VALUES (28, 130000.00, true);
INSERT INTO public.tourist_attractions VALUES (29, 10000.00, true);
INSERT INTO public.tourist_attractions VALUES (30, 10000.00, true);
INSERT INTO public.tourist_attractions VALUES (31, 300000.00, true);
INSERT INTO public.tourist_attractions VALUES (32, 230000.00, true);
INSERT INTO public.tourist_attractions VALUES (33, 220000.00, true);
INSERT INTO public.tourist_attractions VALUES (34, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (35, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (36, 30000.00, true);
INSERT INTO public.tourist_attractions VALUES (37, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (38, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (39, 10000.00, true);
INSERT INTO public.tourist_attractions VALUES (40, 10000.00, true);
INSERT INTO public.tourist_attractions VALUES (41, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (42, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (43, 15000.00, true);
INSERT INTO public.tourist_attractions VALUES (44, 30000.00, true);
INSERT INTO public.tourist_attractions VALUES (45, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (46, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (47, 0.00, false);
INSERT INTO public.tourist_attractions VALUES (48, 50000.00, true);
INSERT INTO public.tourist_attractions VALUES (49, 150000.00, true);
INSERT INTO public.tourist_attractions VALUES (50, 150000.00, true);


--
-- TOC entry 5091 (class 0 OID 39265)
-- Dependencies: 237
-- Data for Name: user_place_favorites; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.user_place_favorites VALUES (1, 110, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (1, 87, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (1, 29, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (2, 124, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (2, 26, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (2, 87, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (3, 23, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (3, 54, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (3, 86, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (3, 53, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (3, 99, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (4, 54, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (4, 106, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (4, 86, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (4, 52, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (4, 70, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (5, 30, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (5, 5, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (5, 78, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (5, 113, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (6, 22, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (6, 48, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (6, 4, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (6, 92, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (7, 74, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (7, 87, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (8, 122, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (8, 71, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (8, 79, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (9, 112, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (9, 125, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (9, 17, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (9, 21, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (9, 63, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (10, 83, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (10, 33, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (10, 108, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (11, 110, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (11, 28, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (11, 5, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (12, 57, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (12, 118, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (12, 94, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (12, 41, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (12, 18, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (13, 116, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (13, 43, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (13, 36, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (13, 100, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (13, 18, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (14, 107, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (14, 31, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (15, 90, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (15, 6, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (15, 114, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (16, 83, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (16, 86, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (16, 17, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (17, 97, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (17, 21, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (17, 76, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (17, 87, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (18, 64, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (18, 54, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (18, 19, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (18, 10, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (18, 79, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (19, 73, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (19, 57, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (19, 51, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (19, 50, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (19, 58, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (20, 39, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (20, 78, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (20, 74, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (21, 119, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (21, 30, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (21, 45, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (21, 122, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (22, 61, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (22, 10, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (22, 1, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (22, 55, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (23, 64, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (23, 126, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (23, 120, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (23, 104, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (24, 107, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (24, 45, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (24, 69, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (25, 83, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (25, 40, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (25, 68, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (26, 47, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (26, 96, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (27, 68, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (27, 123, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (27, 24, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (27, 8, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (27, 9, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (28, 96, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (28, 97, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (28, 90, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (29, 105, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (29, 46, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (29, 57, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (30, 86, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (30, 96, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (30, 113, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (30, 72, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (31, 39, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (31, 94, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (32, 121, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (32, 41, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (32, 74, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (32, 130, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (32, 83, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (33, 14, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (33, 8, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (33, 101, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (34, 101, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (34, 110, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (34, 25, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (35, 2, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (35, 62, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (35, 5, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (36, 57, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (36, 101, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (36, 123, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (36, 75, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (36, 121, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (37, 70, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (37, 15, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (37, 10, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (37, 79, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (37, 71, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (38, 128, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (38, 14, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (38, 22, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (38, 53, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (39, 78, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (39, 112, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (39, 47, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (39, 21, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (40, 55, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (40, 108, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (40, 112, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (40, 60, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (40, 86, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (41, 27, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (41, 71, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (41, 42, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (42, 1, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (42, 117, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (42, 59, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (43, 59, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (43, 98, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (43, 31, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (43, 70, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (43, 63, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (44, 72, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (44, 112, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (44, 52, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (44, 127, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (44, 20, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (45, 23, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (45, 57, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (46, 92, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (46, 22, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (46, 49, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (46, 102, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (47, 19, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (47, 44, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (47, 55, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (47, 129, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (48, 71, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (48, 72, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (48, 28, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (49, 9, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (49, 54, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (49, 25, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (49, 33, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (50, 87, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (50, 45, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (50, 31, '2025-12-25 11:50:50.202358');
INSERT INTO public.user_place_favorites VALUES (50, 93, '2025-12-25 11:50:50.202358');


--
-- TOC entry 5092 (class 0 OID 39281)
-- Dependencies: 238
-- Data for Name: user_post_favorites; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- TOC entry 5075 (class 0 OID 39114)
-- Dependencies: 221
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.users VALUES (1, 'Lê Đức Lan', 'user1@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Lê+Đức+Lan', NULL, 0, true, NULL, NULL, 1, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (2, 'Nguyễn Thị Giang', 'user2@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Nguyễn+Thị+Giang', NULL, 0, true, NULL, NULL, 1, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (3, 'Phan Đức An', 'user3@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phan+Đức+An', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (4, 'Đặng Thanh Chi', 'user4@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Đặng+Thanh+Chi', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (5, 'Võ Hữu Quang', 'user5@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Võ+Hữu+Quang', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (6, 'Vũ Văn Phúc', 'user6@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Vũ+Văn+Phúc', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (7, 'Lê Đức Thảo', 'user7@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Lê+Đức+Thảo', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (8, 'Huỳnh Mạnh Giang', 'user8@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Huỳnh+Mạnh+Giang', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (9, 'Bùi Văn Yến', 'user9@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Bùi+Văn+Yến', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (10, 'Trần Ngọc Em', 'user10@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Trần+Ngọc+Em', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (11, 'Phạm Thanh Thảo', 'user11@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Thanh+Thảo', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (12, 'Trần Minh Oanh', 'user12@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Trần+Minh+Oanh', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (13, 'Phan Minh Minh', 'user13@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phan+Minh+Minh', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (14, 'Vũ Minh Lan', 'user14@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Vũ+Minh+Lan', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (15, 'Võ Đức Khánh', 'user15@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Võ+Đức+Khánh', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (16, 'Bùi Minh Phúc', 'user16@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Bùi+Minh+Phúc', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (17, 'Bùi Đức Chi', 'user17@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Bùi+Đức+Chi', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (18, 'Phạm Ngọc Giang', 'user18@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Ngọc+Giang', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (19, 'Trần Thành Dũng', 'user19@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Trần+Thành+Dũng', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (20, 'Đỗ Hữu Yến', 'user20@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Đỗ+Hữu+Yến', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (21, 'Trần Văn Thảo', 'user21@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Trần+Văn+Thảo', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (22, 'Huỳnh Thị Sơn', 'user22@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Huỳnh+Thị+Sơn', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (23, 'Huỳnh Hữu Thảo', 'user23@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Huỳnh+Hữu+Thảo', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (24, 'Vũ Văn Vinh', 'user24@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Vũ+Văn+Vinh', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (25, 'Phan Thanh Em', 'user25@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phan+Thanh+Em', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (26, 'Võ Thị Bình', 'user26@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Võ+Thị+Bình', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (27, 'Hoàng Thanh Giang', 'user27@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Hoàng+Thanh+Giang', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (28, 'Phan Thị Sơn', 'user28@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phan+Thị+Sơn', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (29, 'Võ Minh Em', 'user29@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Võ+Minh+Em', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (30, 'Nguyễn Thị Yến', 'user30@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Nguyễn+Thị+Yến', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (31, 'Phan Đức Lan', 'user31@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phan+Đức+Lan', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (32, 'Huỳnh Thành Hà', 'user32@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Huỳnh+Thành+Hà', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (33, 'Lê Thanh Hà', 'user33@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Lê+Thanh+Hà', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (34, 'Trần Thanh Giang', 'user34@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Trần+Thanh+Giang', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (35, 'Võ Mạnh Phúc', 'user35@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Võ+Mạnh+Phúc', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (36, 'Phạm Văn Oanh', 'user36@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Văn+Oanh', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (37, 'Trần Văn Hiếu', 'user37@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Trần+Văn+Hiếu', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (38, 'Vũ Thành Lan', 'user38@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Vũ+Thành+Lan', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (39, 'Vũ Thị Em', 'user39@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Vũ+Thị+Em', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (40, 'Phạm Minh Bình', 'user40@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Minh+Bình', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (41, 'Đỗ Minh Ngọc', 'user41@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Đỗ+Minh+Ngọc', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (42, 'Đỗ Minh Yến', 'user42@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Đỗ+Minh+Yến', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (43, 'Phạm Mạnh Hà', 'user43@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Mạnh+Hà', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (44, 'Phạm Minh Giang', 'user44@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Minh+Giang', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (45, 'Phạm Ngọc Minh', 'user45@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Ngọc+Minh', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (46, 'Phạm Đức Ngọc', 'user46@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phạm+Đức+Ngọc', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (47, 'Phan Ngọc Giang', 'user47@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Phan+Ngọc+Giang', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (48, 'Trần Đức Sơn', 'user48@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Trần+Đức+Sơn', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (49, 'Đặng Ngọc Hiếu', 'user49@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Đặng+Ngọc+Hiếu', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');
INSERT INTO public.users VALUES (50, 'Nguyễn Hữu Ngọc', 'user50@example.com', '$2b$12$Kix.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x./.x', 'https://ui-avatars.com/api/?name=Nguyễn+Hữu+Ngọc', NULL, 0, true, NULL, NULL, 2, NULL, '2025-12-25 11:50:50.202358', '2025-12-25 11:50:50.202358');


--
-- TOC entry 5094 (class 0 OID 39290)
-- Dependencies: 240
-- Data for Name: visit_logs; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.visit_logs VALUES (1, 1, 65, NULL, '/places/detail', '192.168.1.65', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (2, 1, 41, NULL, '/places/detail', '192.168.1.40', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (3, 1, 118, NULL, '/places/detail', '192.168.1.193', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (4, 1, 101, NULL, '/places/detail', '192.168.1.135', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (5, 1, 59, NULL, '/places/detail', '192.168.1.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (6, 1, 118, NULL, '/places/detail', '192.168.1.26', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (7, 1, 48, NULL, '/places/detail', '192.168.1.128', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (8, 1, 124, NULL, '/places/detail', '192.168.1.12', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (9, 2, 117, NULL, '/places/detail', '192.168.1.120', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (10, 2, 50, NULL, '/places/detail', '192.168.1.151', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (11, 2, 125, NULL, '/places/detail', '192.168.1.158', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (12, 2, 16, NULL, '/places/detail', '192.168.1.224', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (13, 2, 130, NULL, '/places/detail', '192.168.1.14', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (14, 3, 75, NULL, '/places/detail', '192.168.1.9', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (15, 3, 121, NULL, '/places/detail', '192.168.1.55', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (16, 3, 128, NULL, '/places/detail', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (17, 3, 47, NULL, '/places/detail', '192.168.1.148', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (18, 3, 63, NULL, '/places/detail', '192.168.1.154', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (19, 4, 83, NULL, '/places/detail', '192.168.1.178', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (20, 4, 82, NULL, '/places/detail', '192.168.1.221', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (21, 4, 27, NULL, '/places/detail', '192.168.1.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (22, 4, 110, NULL, '/places/detail', '192.168.1.74', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (23, 4, 47, NULL, '/places/detail', '192.168.1.240', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (24, 4, 21, NULL, '/places/detail', '192.168.1.50', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (25, 4, 37, NULL, '/places/detail', '192.168.1.193', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (26, 5, 7, NULL, '/places/detail', '192.168.1.65', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (27, 5, 39, NULL, '/places/detail', '192.168.1.165', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (28, 5, 15, NULL, '/places/detail', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (29, 5, 77, NULL, '/places/detail', '192.168.1.80', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (30, 5, 88, NULL, '/places/detail', '192.168.1.63', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (31, 5, 10, NULL, '/places/detail', '192.168.1.247', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (32, 5, 20, NULL, '/places/detail', '192.168.1.143', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (33, 5, 78, NULL, '/places/detail', '192.168.1.220', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (34, 5, 86, NULL, '/places/detail', '192.168.1.193', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (35, 6, 35, NULL, '/places/detail', '192.168.1.164', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (36, 6, 32, NULL, '/places/detail', '192.168.1.127', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (37, 6, 104, NULL, '/places/detail', '192.168.1.166', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (38, 6, 2, NULL, '/places/detail', '192.168.1.105', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (39, 6, 94, NULL, '/places/detail', '192.168.1.168', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (40, 6, 16, NULL, '/places/detail', '192.168.1.51', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (41, 6, 37, NULL, '/places/detail', '192.168.1.187', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (42, 6, 114, NULL, '/places/detail', '192.168.1.6', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (43, 7, 51, NULL, '/places/detail', '192.168.1.212', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (44, 7, 20, NULL, '/places/detail', '192.168.1.198', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (45, 7, 1, NULL, '/places/detail', '192.168.1.64', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (46, 7, 121, NULL, '/places/detail', '192.168.1.8', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (47, 7, 92, NULL, '/places/detail', '192.168.1.89', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (48, 7, 106, NULL, '/places/detail', '192.168.1.101', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (49, 7, 35, NULL, '/places/detail', '192.168.1.22', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (50, 8, 9, NULL, '/places/detail', '192.168.1.37', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (51, 8, 18, NULL, '/places/detail', '192.168.1.35', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (52, 8, 65, NULL, '/places/detail', '192.168.1.132', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (53, 8, 55, NULL, '/places/detail', '192.168.1.83', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (54, 8, 114, NULL, '/places/detail', '192.168.1.12', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (55, 9, 3, NULL, '/places/detail', '192.168.1.134', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (56, 9, 128, NULL, '/places/detail', '192.168.1.143', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (57, 9, 106, NULL, '/places/detail', '192.168.1.9', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (58, 9, 104, NULL, '/places/detail', '192.168.1.20', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (59, 9, 38, NULL, '/places/detail', '192.168.1.132', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (60, 9, 128, NULL, '/places/detail', '192.168.1.18', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (61, 10, 117, NULL, '/places/detail', '192.168.1.89', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (62, 10, 31, NULL, '/places/detail', '192.168.1.173', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (63, 10, 60, NULL, '/places/detail', '192.168.1.25', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (64, 10, 79, NULL, '/places/detail', '192.168.1.59', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (65, 10, 98, NULL, '/places/detail', '192.168.1.174', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (66, 10, 84, NULL, '/places/detail', '192.168.1.219', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (67, 10, 91, NULL, '/places/detail', '192.168.1.248', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (68, 11, 19, NULL, '/places/detail', '192.168.1.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (69, 11, 117, NULL, '/places/detail', '192.168.1.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (70, 11, 109, NULL, '/places/detail', '192.168.1.96', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (71, 11, 110, NULL, '/places/detail', '192.168.1.103', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (72, 11, 19, NULL, '/places/detail', '192.168.1.243', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (73, 11, 106, NULL, '/places/detail', '192.168.1.170', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (74, 11, 42, NULL, '/places/detail', '192.168.1.59', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (75, 12, 81, NULL, '/places/detail', '192.168.1.14', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (76, 12, 10, NULL, '/places/detail', '192.168.1.55', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (77, 12, 92, NULL, '/places/detail', '192.168.1.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (78, 12, 2, NULL, '/places/detail', '192.168.1.145', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (79, 12, 107, NULL, '/places/detail', '192.168.1.18', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (80, 12, 59, NULL, '/places/detail', '192.168.1.164', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (81, 12, 126, NULL, '/places/detail', '192.168.1.15', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (82, 12, 85, NULL, '/places/detail', '192.168.1.204', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (83, 12, 45, NULL, '/places/detail', '192.168.1.22', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (84, 13, 102, NULL, '/places/detail', '192.168.1.59', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (85, 13, 130, NULL, '/places/detail', '192.168.1.111', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (86, 13, 2, NULL, '/places/detail', '192.168.1.121', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (87, 13, 112, NULL, '/places/detail', '192.168.1.105', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (88, 13, 93, NULL, '/places/detail', '192.168.1.57', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (89, 13, 10, NULL, '/places/detail', '192.168.1.97', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (90, 13, 10, NULL, '/places/detail', '192.168.1.152', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (91, 13, 22, NULL, '/places/detail', '192.168.1.42', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (92, 13, 6, NULL, '/places/detail', '192.168.1.96', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (93, 14, 66, NULL, '/places/detail', '192.168.1.138', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (94, 14, 117, NULL, '/places/detail', '192.168.1.32', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (95, 14, 130, NULL, '/places/detail', '192.168.1.253', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (96, 14, 49, NULL, '/places/detail', '192.168.1.229', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (97, 14, 42, NULL, '/places/detail', '192.168.1.196', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (98, 14, 63, NULL, '/places/detail', '192.168.1.32', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (99, 14, 59, NULL, '/places/detail', '192.168.1.122', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (100, 14, 104, NULL, '/places/detail', '192.168.1.69', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (101, 14, 130, NULL, '/places/detail', '192.168.1.15', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (102, 15, 15, NULL, '/places/detail', '192.168.1.49', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (103, 15, 27, NULL, '/places/detail', '192.168.1.191', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (104, 15, 84, NULL, '/places/detail', '192.168.1.204', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (105, 15, 100, NULL, '/places/detail', '192.168.1.5', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (106, 15, 77, NULL, '/places/detail', '192.168.1.135', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (107, 16, 24, NULL, '/places/detail', '192.168.1.254', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (108, 16, 77, NULL, '/places/detail', '192.168.1.56', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (109, 16, 23, NULL, '/places/detail', '192.168.1.202', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (110, 16, 54, NULL, '/places/detail', '192.168.1.102', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (111, 16, 77, NULL, '/places/detail', '192.168.1.144', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (112, 16, 2, NULL, '/places/detail', '192.168.1.150', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (113, 17, 63, NULL, '/places/detail', '192.168.1.220', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (114, 17, 74, NULL, '/places/detail', '192.168.1.136', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (115, 17, 99, NULL, '/places/detail', '192.168.1.33', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (116, 17, 22, NULL, '/places/detail', '192.168.1.108', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (117, 17, 65, NULL, '/places/detail', '192.168.1.249', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (118, 17, 115, NULL, '/places/detail', '192.168.1.170', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (119, 17, 12, NULL, '/places/detail', '192.168.1.6', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (120, 17, 79, NULL, '/places/detail', '192.168.1.93', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (121, 18, 57, NULL, '/places/detail', '192.168.1.113', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (122, 18, 113, NULL, '/places/detail', '192.168.1.133', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (123, 18, 58, NULL, '/places/detail', '192.168.1.180', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (124, 18, 74, NULL, '/places/detail', '192.168.1.86', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (125, 18, 96, NULL, '/places/detail', '192.168.1.173', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (126, 18, 72, NULL, '/places/detail', '192.168.1.19', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (127, 18, 102, NULL, '/places/detail', '192.168.1.206', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (128, 18, 39, NULL, '/places/detail', '192.168.1.222', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (129, 19, 68, NULL, '/places/detail', '192.168.1.51', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (130, 19, 18, NULL, '/places/detail', '192.168.1.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (131, 19, 79, NULL, '/places/detail', '192.168.1.91', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (132, 19, 9, NULL, '/places/detail', '192.168.1.111', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (133, 19, 91, NULL, '/places/detail', '192.168.1.61', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (134, 20, 2, NULL, '/places/detail', '192.168.1.91', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (135, 20, 82, NULL, '/places/detail', '192.168.1.139', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (136, 20, 55, NULL, '/places/detail', '192.168.1.169', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (137, 20, 59, NULL, '/places/detail', '192.168.1.198', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (138, 20, 45, NULL, '/places/detail', '192.168.1.148', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (139, 21, 106, NULL, '/places/detail', '192.168.1.60', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (140, 21, 3, NULL, '/places/detail', '192.168.1.173', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (141, 21, 36, NULL, '/places/detail', '192.168.1.94', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (142, 21, 91, NULL, '/places/detail', '192.168.1.179', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (143, 21, 120, NULL, '/places/detail', '192.168.1.228', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (144, 21, 36, NULL, '/places/detail', '192.168.1.6', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (145, 21, 39, NULL, '/places/detail', '192.168.1.226', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (146, 21, 116, NULL, '/places/detail', '192.168.1.169', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (147, 21, 82, NULL, '/places/detail', '192.168.1.193', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (148, 22, 50, NULL, '/places/detail', '192.168.1.54', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (149, 22, 94, NULL, '/places/detail', '192.168.1.96', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (150, 22, 46, NULL, '/places/detail', '192.168.1.175', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (151, 22, 109, NULL, '/places/detail', '192.168.1.160', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (152, 22, 68, NULL, '/places/detail', '192.168.1.162', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (153, 22, 5, NULL, '/places/detail', '192.168.1.67', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (154, 22, 80, NULL, '/places/detail', '192.168.1.226', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (155, 23, 101, NULL, '/places/detail', '192.168.1.187', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (156, 23, 32, NULL, '/places/detail', '192.168.1.22', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (157, 23, 64, NULL, '/places/detail', '192.168.1.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (158, 23, 71, NULL, '/places/detail', '192.168.1.217', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (159, 23, 107, NULL, '/places/detail', '192.168.1.218', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (160, 23, 55, NULL, '/places/detail', '192.168.1.96', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (161, 23, 82, NULL, '/places/detail', '192.168.1.198', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (162, 23, 43, NULL, '/places/detail', '192.168.1.156', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (163, 24, 121, NULL, '/places/detail', '192.168.1.19', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (164, 24, 52, NULL, '/places/detail', '192.168.1.154', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (165, 24, 64, NULL, '/places/detail', '192.168.1.140', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (166, 24, 2, NULL, '/places/detail', '192.168.1.72', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (167, 24, 84, NULL, '/places/detail', '192.168.1.182', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (168, 24, 71, NULL, '/places/detail', '192.168.1.236', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (169, 24, 14, NULL, '/places/detail', '192.168.1.74', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (170, 25, 26, NULL, '/places/detail', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (171, 25, 72, NULL, '/places/detail', '192.168.1.125', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (172, 25, 107, NULL, '/places/detail', '192.168.1.170', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (173, 25, 17, NULL, '/places/detail', '192.168.1.142', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (174, 25, 106, NULL, '/places/detail', '192.168.1.247', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (175, 25, 86, NULL, '/places/detail', '192.168.1.233', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (176, 25, 97, NULL, '/places/detail', '192.168.1.189', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (177, 26, 58, NULL, '/places/detail', '192.168.1.212', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (178, 26, 124, NULL, '/places/detail', '192.168.1.46', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (179, 26, 109, NULL, '/places/detail', '192.168.1.120', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (180, 26, 105, NULL, '/places/detail', '192.168.1.152', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (181, 26, 125, NULL, '/places/detail', '192.168.1.29', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (182, 26, 100, NULL, '/places/detail', '192.168.1.90', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (183, 26, 97, NULL, '/places/detail', '192.168.1.5', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (184, 27, 54, NULL, '/places/detail', '192.168.1.27', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (185, 27, 111, NULL, '/places/detail', '192.168.1.135', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (186, 27, 6, NULL, '/places/detail', '192.168.1.208', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (187, 27, 61, NULL, '/places/detail', '192.168.1.130', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (188, 27, 42, NULL, '/places/detail', '192.168.1.151', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (189, 27, 3, NULL, '/places/detail', '192.168.1.119', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (190, 28, 36, NULL, '/places/detail', '192.168.1.61', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (191, 28, 13, NULL, '/places/detail', '192.168.1.129', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (192, 28, 73, NULL, '/places/detail', '192.168.1.92', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (193, 28, 61, NULL, '/places/detail', '192.168.1.253', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (194, 28, 45, NULL, '/places/detail', '192.168.1.117', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (195, 29, 79, NULL, '/places/detail', '192.168.1.168', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (196, 29, 9, NULL, '/places/detail', '192.168.1.254', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (197, 29, 86, NULL, '/places/detail', '192.168.1.139', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (198, 29, 55, NULL, '/places/detail', '192.168.1.141', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (199, 29, 23, NULL, '/places/detail', '192.168.1.189', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (200, 30, 38, NULL, '/places/detail', '192.168.1.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (201, 30, 17, NULL, '/places/detail', '192.168.1.85', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (202, 30, 26, NULL, '/places/detail', '192.168.1.211', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (203, 30, 10, NULL, '/places/detail', '192.168.1.159', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (204, 30, 66, NULL, '/places/detail', '192.168.1.56', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (205, 31, 22, NULL, '/places/detail', '192.168.1.104', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (206, 31, 98, NULL, '/places/detail', '192.168.1.13', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (207, 31, 16, NULL, '/places/detail', '192.168.1.31', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (208, 31, 67, NULL, '/places/detail', '192.168.1.171', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (209, 31, 101, NULL, '/places/detail', '192.168.1.142', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (210, 31, 100, NULL, '/places/detail', '192.168.1.5', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (211, 32, 25, NULL, '/places/detail', '192.168.1.58', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (212, 32, 97, NULL, '/places/detail', '192.168.1.10', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (213, 32, 56, NULL, '/places/detail', '192.168.1.41', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (214, 32, 107, NULL, '/places/detail', '192.168.1.250', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (215, 32, 66, NULL, '/places/detail', '192.168.1.145', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (216, 32, 80, NULL, '/places/detail', '192.168.1.153', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (217, 32, 17, NULL, '/places/detail', '192.168.1.23', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (218, 32, 100, NULL, '/places/detail', '192.168.1.171', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (219, 32, 101, NULL, '/places/detail', '192.168.1.225', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (220, 33, 91, NULL, '/places/detail', '192.168.1.232', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (221, 33, 38, NULL, '/places/detail', '192.168.1.194', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (222, 33, 93, NULL, '/places/detail', '192.168.1.222', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (223, 33, 88, NULL, '/places/detail', '192.168.1.40', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (224, 33, 38, NULL, '/places/detail', '192.168.1.84', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (225, 33, 20, NULL, '/places/detail', '192.168.1.128', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (226, 33, 82, NULL, '/places/detail', '192.168.1.75', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (227, 33, 38, NULL, '/places/detail', '192.168.1.232', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (228, 33, 50, NULL, '/places/detail', '192.168.1.45', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (229, 34, 30, NULL, '/places/detail', '192.168.1.48', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (230, 34, 99, NULL, '/places/detail', '192.168.1.56', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (231, 34, 10, NULL, '/places/detail', '192.168.1.103', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (232, 34, 62, NULL, '/places/detail', '192.168.1.245', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (233, 34, 63, NULL, '/places/detail', '192.168.1.173', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (234, 34, 87, NULL, '/places/detail', '192.168.1.2', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (235, 34, 112, NULL, '/places/detail', '192.168.1.10', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (236, 34, 107, NULL, '/places/detail', '192.168.1.234', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (237, 34, 29, NULL, '/places/detail', '192.168.1.67', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (238, 35, 126, NULL, '/places/detail', '192.168.1.17', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (239, 35, 11, NULL, '/places/detail', '192.168.1.147', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (240, 35, 79, NULL, '/places/detail', '192.168.1.148', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (241, 35, 3, NULL, '/places/detail', '192.168.1.153', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (242, 35, 17, NULL, '/places/detail', '192.168.1.145', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (243, 35, 95, NULL, '/places/detail', '192.168.1.42', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (244, 35, 25, NULL, '/places/detail', '192.168.1.240', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (245, 36, 97, NULL, '/places/detail', '192.168.1.185', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (246, 36, 87, NULL, '/places/detail', '192.168.1.125', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (247, 36, 22, NULL, '/places/detail', '192.168.1.3', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (248, 36, 35, NULL, '/places/detail', '192.168.1.158', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (249, 36, 2, NULL, '/places/detail', '192.168.1.60', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (250, 36, 130, NULL, '/places/detail', '192.168.1.40', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (251, 36, 18, NULL, '/places/detail', '192.168.1.35', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (252, 37, 65, NULL, '/places/detail', '192.168.1.85', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (253, 37, 19, NULL, '/places/detail', '192.168.1.235', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (254, 37, 82, NULL, '/places/detail', '192.168.1.145', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (255, 37, 117, NULL, '/places/detail', '192.168.1.141', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (256, 37, 24, NULL, '/places/detail', '192.168.1.128', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (257, 37, 22, NULL, '/places/detail', '192.168.1.229', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (258, 37, 41, NULL, '/places/detail', '192.168.1.206', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (259, 37, 107, NULL, '/places/detail', '192.168.1.210', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (260, 37, 121, NULL, '/places/detail', '192.168.1.157', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (261, 38, 33, NULL, '/places/detail', '192.168.1.54', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (262, 38, 92, NULL, '/places/detail', '192.168.1.143', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (263, 38, 54, NULL, '/places/detail', '192.168.1.150', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (264, 38, 4, NULL, '/places/detail', '192.168.1.179', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (265, 38, 54, NULL, '/places/detail', '192.168.1.94', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (266, 39, 25, NULL, '/places/detail', '192.168.1.30', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (267, 39, 46, NULL, '/places/detail', '192.168.1.246', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (268, 39, 8, NULL, '/places/detail', '192.168.1.91', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (269, 39, 91, NULL, '/places/detail', '192.168.1.28', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (270, 39, 116, NULL, '/places/detail', '192.168.1.5', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (271, 40, 39, NULL, '/places/detail', '192.168.1.161', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (272, 40, 59, NULL, '/places/detail', '192.168.1.123', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (273, 40, 75, NULL, '/places/detail', '192.168.1.22', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (274, 40, 83, NULL, '/places/detail', '192.168.1.229', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (275, 40, 126, NULL, '/places/detail', '192.168.1.126', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (276, 40, 56, NULL, '/places/detail', '192.168.1.107', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (277, 40, 23, NULL, '/places/detail', '192.168.1.89', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (278, 41, 111, NULL, '/places/detail', '192.168.1.7', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (279, 41, 105, NULL, '/places/detail', '192.168.1.61', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (280, 41, 22, NULL, '/places/detail', '192.168.1.138', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (281, 41, 49, NULL, '/places/detail', '192.168.1.201', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (282, 41, 84, NULL, '/places/detail', '192.168.1.167', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (283, 41, 44, NULL, '/places/detail', '192.168.1.35', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (284, 42, 100, NULL, '/places/detail', '192.168.1.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (285, 42, 117, NULL, '/places/detail', '192.168.1.67', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (286, 42, 88, NULL, '/places/detail', '192.168.1.134', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (287, 42, 91, NULL, '/places/detail', '192.168.1.236', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (288, 42, 52, NULL, '/places/detail', '192.168.1.35', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (289, 42, 63, NULL, '/places/detail', '192.168.1.107', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (290, 42, 8, NULL, '/places/detail', '192.168.1.40', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (291, 42, 100, NULL, '/places/detail', '192.168.1.133', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (292, 43, 115, NULL, '/places/detail', '192.168.1.18', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (293, 43, 84, NULL, '/places/detail', '192.168.1.6', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (294, 43, 111, NULL, '/places/detail', '192.168.1.246', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (295, 43, 31, NULL, '/places/detail', '192.168.1.228', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (296, 43, 28, NULL, '/places/detail', '192.168.1.150', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (297, 43, 91, NULL, '/places/detail', '192.168.1.27', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (298, 43, 19, NULL, '/places/detail', '192.168.1.215', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (299, 43, 5, NULL, '/places/detail', '192.168.1.26', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (300, 44, 45, NULL, '/places/detail', '192.168.1.205', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (301, 44, 3, NULL, '/places/detail', '192.168.1.236', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (302, 44, 48, NULL, '/places/detail', '192.168.1.9', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (303, 44, 39, NULL, '/places/detail', '192.168.1.146', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (304, 44, 63, NULL, '/places/detail', '192.168.1.111', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (305, 44, 97, NULL, '/places/detail', '192.168.1.19', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (306, 44, 30, NULL, '/places/detail', '192.168.1.73', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (307, 44, 114, NULL, '/places/detail', '192.168.1.178', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (308, 44, 48, NULL, '/places/detail', '192.168.1.201', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (309, 45, 24, NULL, '/places/detail', '192.168.1.86', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (310, 45, 15, NULL, '/places/detail', '192.168.1.67', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (311, 45, 34, NULL, '/places/detail', '192.168.1.99', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (312, 45, 109, NULL, '/places/detail', '192.168.1.136', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (313, 45, 75, NULL, '/places/detail', '192.168.1.118', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (314, 45, 107, NULL, '/places/detail', '192.168.1.228', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (315, 46, 58, NULL, '/places/detail', '192.168.1.60', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (316, 46, 7, NULL, '/places/detail', '192.168.1.134', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (317, 46, 81, NULL, '/places/detail', '192.168.1.74', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (318, 46, 22, NULL, '/places/detail', '192.168.1.45', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (319, 46, 44, NULL, '/places/detail', '192.168.1.250', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (320, 46, 58, NULL, '/places/detail', '192.168.1.66', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (321, 47, 66, NULL, '/places/detail', '192.168.1.236', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (322, 47, 103, NULL, '/places/detail', '192.168.1.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (323, 47, 35, NULL, '/places/detail', '192.168.1.193', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (324, 47, 108, NULL, '/places/detail', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (325, 47, 72, NULL, '/places/detail', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (326, 48, 77, NULL, '/places/detail', '192.168.1.238', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (327, 48, 100, NULL, '/places/detail', '192.168.1.40', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (328, 48, 41, NULL, '/places/detail', '192.168.1.108', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (329, 48, 31, NULL, '/places/detail', '192.168.1.58', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (330, 48, 82, NULL, '/places/detail', '192.168.1.141', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (331, 48, 85, NULL, '/places/detail', '192.168.1.9', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (332, 49, 19, NULL, '/places/detail', '192.168.1.85', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (333, 49, 45, NULL, '/places/detail', '192.168.1.117', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (334, 49, 16, NULL, '/places/detail', '192.168.1.174', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (335, 49, 53, NULL, '/places/detail', '192.168.1.188', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (336, 49, 9, NULL, '/places/detail', '192.168.1.55', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (337, 49, 34, NULL, '/places/detail', '192.168.1.14', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (338, 49, 92, NULL, '/places/detail', '192.168.1.41', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (339, 49, 56, NULL, '/places/detail', '192.168.1.179', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (340, 50, 3, NULL, '/places/detail', '192.168.1.39', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (341, 50, 111, NULL, '/places/detail', '192.168.1.97', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (342, 50, 110, NULL, '/places/detail', '192.168.1.68', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (343, 50, 106, NULL, '/places/detail', '192.168.1.56', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');
INSERT INTO public.visit_logs VALUES (344, 50, 52, NULL, '/places/detail', '192.168.1.73', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-25 11:50:50.202358');


--
-- TOC entry 5112 (class 0 OID 0)
-- Dependencies: 222
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 1, false);


--
-- TOC entry 5113 (class 0 OID 0)
-- Dependencies: 226
-- Name: districts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.districts_id_seq', 16, true);


--
-- TOC entry 5114 (class 0 OID 0)
-- Dependencies: 232
-- Name: place_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.place_images_id_seq', 376, true);


--
-- TOC entry 5115 (class 0 OID 0)
-- Dependencies: 228
-- Name: place_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.place_types_id_seq', 3, true);


--
-- TOC entry 5116 (class 0 OID 0)
-- Dependencies: 230
-- Name: places_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.places_id_seq', 130, true);


--
-- TOC entry 5117 (class 0 OID 0)
-- Dependencies: 218
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.roles_id_seq', 2, true);


--
-- TOC entry 5118 (class 0 OID 0)
-- Dependencies: 224
-- Name: token_refresh_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.token_refresh_id_seq', 1, false);


--
-- TOC entry 5119 (class 0 OID 0)
-- Dependencies: 220
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 50, true);


--
-- TOC entry 5120 (class 0 OID 0)
-- Dependencies: 239
-- Name: visit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.visit_logs_id_seq', 344, true);


--
-- TOC entry 4877 (class 2606 OID 39142)
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4885 (class 2606 OID 39176)
-- Name: districts districts_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.districts
    ADD CONSTRAINT districts_name_key UNIQUE (name);


--
-- TOC entry 4887 (class 2606 OID 39174)
-- Name: districts districts_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.districts
    ADD CONSTRAINT districts_pkey PRIMARY KEY (id);


--
-- TOC entry 4903 (class 2606 OID 39248)
-- Name: hotels hotels_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hotels
    ADD CONSTRAINT hotels_pkey PRIMARY KEY (place_id);


--
-- TOC entry 4899 (class 2606 OID 39226)
-- Name: place_images place_images_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.place_images
    ADD CONSTRAINT place_images_pkey PRIMARY KEY (id);


--
-- TOC entry 4889 (class 2606 OID 39185)
-- Name: place_types place_types_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.place_types
    ADD CONSTRAINT place_types_name_key UNIQUE (name);


--
-- TOC entry 4891 (class 2606 OID 39183)
-- Name: place_types place_types_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.place_types
    ADD CONSTRAINT place_types_pkey PRIMARY KEY (id);


--
-- TOC entry 4897 (class 2606 OID 39201)
-- Name: places places_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_pkey PRIMARY KEY (id);


--
-- TOC entry 4901 (class 2606 OID 39238)
-- Name: restaurants restaurants_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_pkey PRIMARY KEY (place_id);


--
-- TOC entry 4869 (class 2606 OID 39110)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 4871 (class 2606 OID 39112)
-- Name: roles roles_role_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);


--
-- TOC entry 4881 (class 2606 OID 39159)
-- Name: token_refresh token_refresh_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.token_refresh
    ADD CONSTRAINT token_refresh_pkey PRIMARY KEY (id);


--
-- TOC entry 4883 (class 2606 OID 39161)
-- Name: token_refresh token_refresh_refresh_token_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.token_refresh
    ADD CONSTRAINT token_refresh_refresh_token_key UNIQUE (refresh_token);


--
-- TOC entry 4905 (class 2606 OID 39259)
-- Name: tourist_attractions tourist_attractions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tourist_attractions
    ADD CONSTRAINT tourist_attractions_pkey PRIMARY KEY (place_id);


--
-- TOC entry 4907 (class 2606 OID 39270)
-- Name: user_place_favorites user_place_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_place_favorites
    ADD CONSTRAINT user_place_favorites_pkey PRIMARY KEY (user_id, place_id);


--
-- TOC entry 4909 (class 2606 OID 39288)
-- Name: user_post_favorites user_post_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_post_favorites
    ADD CONSTRAINT user_post_favorites_pkey PRIMARY KEY (user_id, post_id);


--
-- TOC entry 4873 (class 2606 OID 39127)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4875 (class 2606 OID 39125)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4913 (class 2606 OID 39298)
-- Name: visit_logs visit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.visit_logs
    ADD CONSTRAINT visit_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4878 (class 1259 OID 39148)
-- Name: idx_activity_logs_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_activity_logs_user ON public.activity_logs USING btree (user_id);


--
-- TOC entry 4892 (class 1259 OID 39212)
-- Name: idx_places_district; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_places_district ON public.places USING btree (district_id);


--
-- TOC entry 4893 (class 1259 OID 39215)
-- Name: idx_places_location; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_places_location ON public.places USING btree (latitude, longitude);


--
-- TOC entry 4894 (class 1259 OID 39214)
-- Name: idx_places_rating; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_places_rating ON public.places USING btree (rating_average);


--
-- TOC entry 4895 (class 1259 OID 39213)
-- Name: idx_places_type; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_places_type ON public.places USING btree (place_type_id);


--
-- TOC entry 4879 (class 1259 OID 39167)
-- Name: idx_token_refresh_expires_at; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_token_refresh_expires_at ON public.token_refresh USING btree (expires_at);


--
-- TOC entry 4910 (class 1259 OID 39310)
-- Name: idx_visit_logs_place; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_visit_logs_place ON public.visit_logs USING btree (place_id);


--
-- TOC entry 4911 (class 1259 OID 39309)
-- Name: idx_visit_logs_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_visit_logs_user ON public.visit_logs USING btree (user_id);


--
-- TOC entry 4915 (class 2606 OID 39143)
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4921 (class 2606 OID 39249)
-- Name: hotels hotels_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hotels
    ADD CONSTRAINT hotels_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id) ON DELETE CASCADE;


--
-- TOC entry 4919 (class 2606 OID 39227)
-- Name: place_images place_images_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.place_images
    ADD CONSTRAINT place_images_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id);


--
-- TOC entry 4917 (class 2606 OID 39207)
-- Name: places places_district_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_district_id_fkey FOREIGN KEY (district_id) REFERENCES public.districts(id);


--
-- TOC entry 4918 (class 2606 OID 39202)
-- Name: places places_place_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.places
    ADD CONSTRAINT places_place_type_id_fkey FOREIGN KEY (place_type_id) REFERENCES public.place_types(id);


--
-- TOC entry 4920 (class 2606 OID 39239)
-- Name: restaurants restaurants_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id) ON DELETE CASCADE;


--
-- TOC entry 4916 (class 2606 OID 39162)
-- Name: token_refresh token_refresh_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.token_refresh
    ADD CONSTRAINT token_refresh_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4922 (class 2606 OID 39260)
-- Name: tourist_attractions tourist_attractions_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tourist_attractions
    ADD CONSTRAINT tourist_attractions_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id) ON DELETE CASCADE;


--
-- TOC entry 4923 (class 2606 OID 39276)
-- Name: user_place_favorites user_place_favorites_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_place_favorites
    ADD CONSTRAINT user_place_favorites_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id);


--
-- TOC entry 4924 (class 2606 OID 39271)
-- Name: user_place_favorites user_place_favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_place_favorites
    ADD CONSTRAINT user_place_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4914 (class 2606 OID 39128)
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- TOC entry 4925 (class 2606 OID 39304)
-- Name: visit_logs visit_logs_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.visit_logs
    ADD CONSTRAINT visit_logs_place_id_fkey FOREIGN KEY (place_id) REFERENCES public.places(id);


--
-- TOC entry 4926 (class 2606 OID 39299)
-- Name: visit_logs visit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.visit_logs
    ADD CONSTRAINT visit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 5101 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: admin
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


-- Completed on 2025-12-25 13:07:01

--
-- PostgreSQL database dump complete
--

