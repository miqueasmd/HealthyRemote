--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activities; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.activities (
    id integer NOT NULL,
    user_id integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    activity_type character varying(50),
    duration integer,
    CONSTRAINT duration_check CHECK ((duration > 0))
);


ALTER TABLE public.activities OWNER TO neondb_owner;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activities_id_seq OWNER TO neondb_owner;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.id;


--
-- Name: assessments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.assessments (
    id integer NOT NULL,
    user_id integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    stress_score integer,
    bmi double precision,
    activity_level character varying(50),
    physical_score integer,
    pain_points jsonb,
    CONSTRAINT stress_score_range CHECK (((stress_score >= 0) AND (stress_score <= 10)))
);


ALTER TABLE public.assessments OWNER TO neondb_owner;

--
-- Name: assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assessments_id_seq OWNER TO neondb_owner;

--
-- Name: assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.assessments_id_seq OWNED BY public.assessments.id;


--
-- Name: challenges; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.challenges (
    id integer NOT NULL,
    user_id integer,
    challenge_name character varying(100),
    start_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    end_date timestamp without time zone,
    status character varying(20) DEFAULT 'active'::character varying,
    progress jsonb
);


ALTER TABLE public.challenges OWNER TO neondb_owner;

--
-- Name: challenges_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.challenges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.challenges_id_seq OWNER TO neondb_owner;

--
-- Name: challenges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.challenges_id_seq OWNED BY public.challenges.id;


--
-- Name: mobility_tests; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.mobility_tests (
    id integer NOT NULL,
    user_id integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    test_name character varying(50),
    score character varying(50),
    notes text
);


ALTER TABLE public.mobility_tests OWNER TO neondb_owner;

--
-- Name: mobility_tests_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.mobility_tests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mobility_tests_id_seq OWNER TO neondb_owner;

--
-- Name: mobility_tests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.mobility_tests_id_seq OWNED BY public.mobility_tests.id;


--
-- Name: stress_logs; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.stress_logs (
    id integer NOT NULL,
    user_id integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    stress_score integer,
    CONSTRAINT stress_log_score_range CHECK (((stress_score >= 0) AND (stress_score <= 10)))
);


ALTER TABLE public.stress_logs OWNER TO neondb_owner;

--
-- Name: stress_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.stress_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stress_logs_id_seq OWNER TO neondb_owner;

--
-- Name: stress_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.stress_logs_id_seq OWNED BY public.stress_logs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.users (
    id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    name character varying(100),
    email character varying(255)
);


ALTER TABLE public.users OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: weight_logs; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.weight_logs (
    id integer NOT NULL,
    user_id integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    weight double precision,
    CONSTRAINT weight_check CHECK ((weight > (0)::double precision))
);


ALTER TABLE public.weight_logs OWNER TO neondb_owner;

--
-- Name: weight_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.weight_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.weight_logs_id_seq OWNER TO neondb_owner;

--
-- Name: weight_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.weight_logs_id_seq OWNED BY public.weight_logs.id;


--
-- Name: activities id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.activities ALTER COLUMN id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- Name: assessments id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessments ALTER COLUMN id SET DEFAULT nextval('public.assessments_id_seq'::regclass);


--
-- Name: challenges id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.challenges ALTER COLUMN id SET DEFAULT nextval('public.challenges_id_seq'::regclass);


--
-- Name: mobility_tests id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.mobility_tests ALTER COLUMN id SET DEFAULT nextval('public.mobility_tests_id_seq'::regclass);


--
-- Name: stress_logs id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.stress_logs ALTER COLUMN id SET DEFAULT nextval('public.stress_logs_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: weight_logs id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.weight_logs ALTER COLUMN id SET DEFAULT nextval('public.weight_logs_id_seq'::regclass);


--
-- Data for Name: activities; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.activities (id, user_id, date, activity_type, duration) FROM stdin;
1	1	2025-02-12 08:24:58.341286	Walking	15
2	1	2025-02-12 08:25:10.554274	Stretching	15
3	2	2025-02-12 08:34:02.156706	walking	15
4	2	2025-02-12 08:41:08.087972	stretching	15
5	2	2025-02-12 08:49:32.605757	exercise	15
6	2	2025-02-12 14:00:14.091305	standing	15
7	4	2025-02-12 21:03:28.24763	walking	15
8	4	2025-02-12 21:03:36.793096	exercise	30
9	5	2025-02-13 19:26:47.733699	walking	15
10	5	2025-02-13 19:26:56.347615	exercise	20
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.assessments (id, user_id, date, stress_score, bmi, activity_level, physical_score, pain_points) FROM stdin;
1	1	2025-02-12 08:23:09.58118	5	24.2	light	0	{"back": "none", "head": "none", "neck": "none", "wrists": "none", "shoulders": "none"}
2	1	2025-02-12 08:26:29.257295	5	24.2	light	5	{"back": "mild", "head": "mild", "neck": "mild", "wrists": "mild", "shoulders": "mild"}
3	1	2025-02-12 08:30:45.33361	5	24.2	light	2	{"back": "none", "head": "moderate", "neck": "none", "wrists": "none", "shoulders": "none"}
4	2	2025-02-12 08:33:46.172313	5	24.2	light	0	{"back": "none", "head": "none", "neck": "none", "wrists": "none", "shoulders": "none"}
5	3	2025-02-12 08:35:25.873891	5	24.2	light	5	{"back": "mild", "head": "mild", "neck": "mild", "wrists": "mild", "shoulders": "mild"}
6	2	2025-02-12 08:40:41.102558	5	24.2	light	0	{"back": "none", "head": "none", "neck": "none", "wrists": "none", "shoulders": "none"}
7	2	2025-02-12 08:49:21.496737	5	24.2	light	0	{"back": "none", "head": "none", "neck": "none", "wrists": "none", "shoulders": "none"}
8	2	2025-02-12 13:24:20.762558	4	24.2	light	0	{"back": "none", "head": "none", "neck": "none", "wrists": "none", "shoulders": "none"}
9	2	2025-02-12 13:56:15.467753	5	24.2	light	6	{"back": "none", "head": "severe", "neck": "none", "wrists": "severe", "shoulders": "none"}
10	2	2025-02-12 13:59:06.378013	7	24.2	vigorous	2	{"back": "none", "head": "moderate", "neck": "none", "wrists": "none", "shoulders": "none"}
11	4	2025-02-12 21:01:59.583062	7	24	moderate	5	{"back": "none", "head": "severe", "neck": "moderate", "wrists": "none", "shoulders": "none"}
12	5	2025-02-13 19:24:55.454697	1	21.6	sedentary	4	{"back": "mild", "head": "mild", "neck": "moderate", "wrists": "none", "shoulders": "none"}
13	5	2025-02-13 19:25:55.870553	10	35.4	sedentary	15	{"back": "severe", "head": "severe", "neck": "severe", "wrists": "severe", "shoulders": "severe"}
\.


--
-- Data for Name: challenges; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.challenges (id, user_id, challenge_name, start_date, end_date, status, progress) FROM stdin;
3	2	Movement Boost	2025-02-12 08:50:11.263057	2025-02-17 08:50:11.263057	active	{"current_day": 2, "completed_tasks": ["Move 10min"]}
2	2	Stress-Free Week	2025-02-12 08:50:08.668259	2025-02-19 08:50:08.668259	active	{"current_day": 2, "completed_tasks": ["Meditate 10min"]}
1	2	7-Day Posture Challenge	2025-02-12 08:50:05.657184	2025-02-19 08:50:05.657184	active	{"current_day": 2, "completed_tasks": ["Check my posture"]}
6	4	Movement Boost	2025-02-12 21:05:17.010492	2025-02-17 21:05:17.010492	active	{"current_day": 2, "completed_tasks": ["Training 20min this morning"]}
5	4	Stress-Free Week	2025-02-12 21:05:10.048835	2025-02-19 21:05:10.048835	active	{"current_day": 2, "completed_tasks": ["Meditated 5min after work"]}
4	4	7-Day Posture Challenge	2025-02-12 21:05:01.290085	2025-02-19 21:05:01.290085	active	{"current_day": 2, "completed_tasks": ["3 blades exercises"]}
7	5	7-Day Posture Challenge	2025-02-13 19:29:20.038905	2025-02-20 19:29:20.038905	active	{"current_day": 1, "completed_tasks": []}
8	5	Stress-Free Week	2025-02-13 19:29:23.078597	2025-02-20 19:29:23.078597	active	{"current_day": 1, "completed_tasks": []}
9	5	Movement Boost	2025-02-13 19:29:25.846644	2025-02-18 19:29:25.846644	active	{"current_day": 3, "completed_tasks": ["10 min walking", "3 blades squezes"]}
\.


--
-- Data for Name: mobility_tests; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.mobility_tests (id, user_id, date, test_name, score, notes) FROM stdin;
1	2	2025-02-12 08:51:40.375226	Neck Mobility	Excellent	All good
2	2	2025-02-12 08:51:49.197913	Shoulder Mobility	Fair	
3	2	2025-02-12 08:51:55.414307	Wrist Flexibility	Poor	
4	5	2025-02-13 19:28:34.714655	Neck Mobility	Excellent	
5	5	2025-02-13 19:28:43.005958	Shoulder Mobility	Poor	
6	5	2025-02-13 19:28:56.832755	Wrist Flexibility	Fair	
\.


--
-- Data for Name: stress_logs; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.stress_logs (id, user_id, date, stress_score) FROM stdin;
1	1	2025-02-12 08:23:22.797727	5
2	1	2025-02-12 08:26:48.656179	6
3	2	2025-02-12 08:33:57.848324	5
4	2	2025-02-12 08:41:00.893153	6
5	2	2025-02-12 13:59:36.825189	4
6	2	2025-02-12 13:59:55.214552	6
7	4	2025-02-12 21:03:07.404016	7
8	4	2025-02-12 21:03:19.622858	8
9	5	2025-02-13 19:26:24.351606	1
10	5	2025-02-13 19:26:37.700261	10
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.users (id, created_at, name, email) FROM stdin;
1	2025-02-12 08:19:58.064139	\N	\N
2	2025-02-12 08:33:34.478406	Paco	paco@example.com
3	2025-02-12 08:35:12.059993	Paca	paca@example.com
4	2025-02-12 20:58:47.070131	Fabiola	fabiola@example.com
5	2025-02-13 19:22:44.124094	Diana	diana@example.com
\.


--
-- Data for Name: weight_logs; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.weight_logs (id, user_id, date, weight) FROM stdin;
1	1	2025-02-12 08:25:28.618202	70
2	1	2025-02-12 08:30:54.806963	70
3	2	2025-02-12 08:34:05.897265	70
4	2	2025-02-12 08:41:17.65934	71
5	2	2025-02-12 08:49:51.096229	69
6	4	2025-02-12 21:03:45.671313	54
7	5	2025-02-13 19:27:04.726943	61
8	5	2025-02-13 19:27:11.651684	100
\.


--
-- Name: activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.activities_id_seq', 10, true);


--
-- Name: assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.assessments_id_seq', 13, true);


--
-- Name: challenges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.challenges_id_seq', 9, true);


--
-- Name: mobility_tests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.mobility_tests_id_seq', 6, true);


--
-- Name: stress_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.stress_logs_id_seq', 10, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- Name: weight_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.weight_logs_id_seq', 8, true);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: assessments assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_pkey PRIMARY KEY (id);


--
-- Name: challenges challenges_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.challenges
    ADD CONSTRAINT challenges_pkey PRIMARY KEY (id);


--
-- Name: mobility_tests mobility_tests_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.mobility_tests
    ADD CONSTRAINT mobility_tests_pkey PRIMARY KEY (id);


--
-- Name: stress_logs stress_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.stress_logs
    ADD CONSTRAINT stress_logs_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: weight_logs weight_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.weight_logs
    ADD CONSTRAINT weight_logs_pkey PRIMARY KEY (id);


--
-- Name: activities activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: assessments assessments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: challenges challenges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.challenges
    ADD CONSTRAINT challenges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: mobility_tests mobility_tests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.mobility_tests
    ADD CONSTRAINT mobility_tests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stress_logs stress_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.stress_logs
    ADD CONSTRAINT stress_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: weight_logs weight_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.weight_logs
    ADD CONSTRAINT weight_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- neondb_ownerQL database dump complete
--

