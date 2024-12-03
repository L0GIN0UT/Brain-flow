--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: clinic; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clinic (
    uuid uuid NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(100),
    logo bytea
);


ALTER TABLE public.clinic OWNER TO postgres;

--
-- Name: clinicaddress; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clinicaddress (
    uuid uuid NOT NULL,
    region character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    street character varying(100) NOT NULL,
    build character varying(100),
    phone character varying(20),
    email character varying(255),
    clinic_uuid uuid NOT NULL
);


ALTER TABLE public.clinicaddress OWNER TO postgres;

--
-- Name: desyncdatas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.desyncdatas (
    uuid uuid NOT NULL,
    data json,
    date timestamp with time zone,
    device_uuid uuid NOT NULL,
    user_uuid uuid NOT NULL,
    patient_uuid uuid NOT NULL,
    type_research_uuid uuid NOT NULL
);


ALTER TABLE public.desyncdatas OWNER TO postgres;

--
-- Name: device; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.device (
    uuid uuid NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(100),
    clinic_uuid uuid NOT NULL,
    device_types_uuid uuid
);


ALTER TABLE public.device OWNER TO postgres;

--
-- Name: device_device_type_link; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.device_device_type_link (
    device_uuid uuid NOT NULL,
    device_types_uuid uuid NOT NULL
);


ALTER TABLE public.device_device_type_link OWNER TO postgres;

--
-- Name: devicetype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.devicetype (
    uuid uuid NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(100)
);


ALTER TABLE public.devicetype OWNER TO postgres;

--
-- Name: patient; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patient (
    uuid uuid NOT NULL,
    code character varying(100) NOT NULL,
    diagnosis character varying(100),
    clinic_uuid uuid NOT NULL
);


ALTER TABLE public.patient OWNER TO postgres;

--
-- Name: typeresearch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.typeresearch (
    uuid uuid NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(100)
);


ALTER TABLE public.typeresearch OWNER TO postgres;

--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    uuid uuid NOT NULL,
    password character varying NOT NULL,
    last_name character varying(100),
    first_name character varying(100),
    patronymic character varying(100),
    phone character varying(20),
    email character varying(255) NOT NULL,
    avatar bytea,
    clinic_uuid uuid NOT NULL
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- Data for Name: clinic; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clinic (uuid, name, description, logo) FROM stdin;
e8145343-c75c-4dfc-8c4a-7640b9ef43ae	Клиника 0	тестовая клиника для обновления и удаления	\N
56e4c010-816a-4ce6-910d-84cb9616b63d	Клиника -1	тестовая клиника для подключения к ней всего и вся	\N
\.


--
-- Data for Name: clinicaddress; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clinicaddress (uuid, region, city, street, build, phone, email, clinic_uuid) FROM stdin;
b02a4c7f-67ac-4f86-b63b-1ed0b8be78a0	Лупье	Пупье	Ковыльчетый бульвар	17	\N	user@example.com	56e4c010-816a-4ce6-910d-84cb9616b63d
\.


--
-- Data for Name: desyncdatas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.desyncdatas (uuid, data, date, device_uuid, user_uuid, patient_uuid, type_research_uuid) FROM stdin;
50f987c5-235c-4190-9d61-b51158f23661	{}	2023-10-27 06:44:08.898+00	cb19caae-32aa-436b-b14b-ef80f1c3243e	484b25ca-2151-4afa-9ea6-a3ad75e707f9	044a8465-7c3b-4d87-86a9-06b7289fac6f	7fa1aae8-0fc9-4eb1-97ee-fd972ed10ebe
\.


--
-- Data for Name: device; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.device (uuid, name, description, clinic_uuid, device_types_uuid) FROM stdin;
104ebe27-195e-4772-8a90-dd2f13b7fa4e	Девайс 0	Девайс для тестов обновления и удаления	56e4c010-816a-4ce6-910d-84cb9616b63d	\N
cb19caae-32aa-436b-b14b-ef80f1c3243e	Девайс -1	Девайс для тестов dysyncdata	56e4c010-816a-4ce6-910d-84cb9616b63d	\N
\.


--
-- Data for Name: device_device_type_link; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.device_device_type_link (device_uuid, device_types_uuid) FROM stdin;
\.


--
-- Data for Name: devicetype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.devicetype (uuid, name, description) FROM stdin;
14ec85c1-e3dd-493a-b4ea-ecc80ba530ea	Тип девайсов 0	тестовый тип девайсов для обновления и удаления
\.


--
-- Data for Name: patient; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patient (uuid, code, diagnosis, clinic_uuid) FROM stdin;
dfcb3752-57db-470c-9156-702aca2015b7	Тестовый пациент 0	Пациент для тестов обновления и удаления	56e4c010-816a-4ce6-910d-84cb9616b63d
044a8465-7c3b-4d87-86a9-06b7289fac6f	Тестовый пациент -1	Пациент для тестов dysyncdata	56e4c010-816a-4ce6-910d-84cb9616b63d
\.


--
-- Data for Name: typeresearch; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.typeresearch (uuid, name, description) FROM stdin;
71774db0-d97c-4b6c-a888-917247076315	Тип исследования 0	Тестовый тип исследования для обновления и удаления
7fa1aae8-0fc9-4eb1-97ee-fd972ed10ebe	Тип исследования -1	Тестовый тип исследования для dysyncdata 
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (uuid, password, last_name, first_name, patronymic, phone, email, avatar, clinic_uuid) FROM stdin;
4fd8d69d-1352-484a-b83a-905af35c8412	FsMqSoAhuOql$b3900d883a8da03808ef7e4701fc4319e0eb6cd9a3812e2088bfde14ecdb9d8d	Мусин	пароль 123	Пусин	\N	test@desync.com	\N	56e4c010-816a-4ce6-910d-84cb9616b63d
484b25ca-2151-4afa-9ea6-a3ad75e707f9	GTcNshQRWcXt$9f37267b4b27912d5cfb1b6936a17109d01f3bf029c493b384944768a52cf417	Хусейн	пароль 1234	Для тестов dysyncdata 	\N	1test@desync.com	\N	56e4c010-816a-4ce6-910d-84cb9616b63d
\.


--
-- Name: clinic clinic_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clinic
    ADD CONSTRAINT clinic_name_key UNIQUE (name);


--
-- Name: clinic clinic_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clinic
    ADD CONSTRAINT clinic_pkey PRIMARY KEY (uuid);


--
-- Name: clinicaddress clinicaddress_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clinicaddress
    ADD CONSTRAINT clinicaddress_phone_key UNIQUE (phone);


--
-- Name: clinicaddress clinicaddress_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clinicaddress
    ADD CONSTRAINT clinicaddress_pkey PRIMARY KEY (uuid);


--
-- Name: desyncdatas desyncdatas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desyncdatas
    ADD CONSTRAINT desyncdatas_pkey PRIMARY KEY (uuid);


--
-- Name: device_device_type_link device_device_type_link_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_device_type_link
    ADD CONSTRAINT device_device_type_link_pkey PRIMARY KEY (device_uuid, device_types_uuid);


--
-- Name: device device_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_name_key UNIQUE (name);


--
-- Name: device device_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_pkey PRIMARY KEY (uuid);


--
-- Name: devicetype devicetype_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devicetype
    ADD CONSTRAINT devicetype_name_key UNIQUE (name);


--
-- Name: devicetype devicetype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devicetype
    ADD CONSTRAINT devicetype_pkey PRIMARY KEY (uuid);


--
-- Name: patient patient_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT patient_code_key UNIQUE (code);


--
-- Name: patient patient_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT patient_pkey PRIMARY KEY (uuid);


--
-- Name: typeresearch typeresearch_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.typeresearch
    ADD CONSTRAINT typeresearch_name_key UNIQUE (name);


--
-- Name: typeresearch typeresearch_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.typeresearch
    ADD CONSTRAINT typeresearch_pkey PRIMARY KEY (uuid);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_phone_key UNIQUE (phone);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (uuid);


--
-- Name: ix_desyncdatas_patient_uuid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_desyncdatas_patient_uuid ON public.desyncdatas USING btree (patient_uuid);


--
-- Name: ix_desyncdatas_user_uuid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_desyncdatas_user_uuid ON public.desyncdatas USING btree (user_uuid);


--
-- Name: clinicaddress clinicaddress_clinic_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clinicaddress
    ADD CONSTRAINT clinicaddress_clinic_uuid_fkey FOREIGN KEY (clinic_uuid) REFERENCES public.clinic(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: desyncdatas desyncdatas_device_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desyncdatas
    ADD CONSTRAINT desyncdatas_device_uuid_fkey FOREIGN KEY (device_uuid) REFERENCES public.device(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: desyncdatas desyncdatas_patient_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desyncdatas
    ADD CONSTRAINT desyncdatas_patient_uuid_fkey FOREIGN KEY (patient_uuid) REFERENCES public.patient(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: desyncdatas desyncdatas_type_research_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desyncdatas
    ADD CONSTRAINT desyncdatas_type_research_uuid_fkey FOREIGN KEY (type_research_uuid) REFERENCES public.typeresearch(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: desyncdatas desyncdatas_user_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.desyncdatas
    ADD CONSTRAINT desyncdatas_user_uuid_fkey FOREIGN KEY (user_uuid) REFERENCES public."user"(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: device device_clinic_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_clinic_uuid_fkey FOREIGN KEY (clinic_uuid) REFERENCES public.clinic(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: device_device_type_link device_device_type_link_device_types_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_device_type_link
    ADD CONSTRAINT device_device_type_link_device_types_uuid_fkey FOREIGN KEY (device_types_uuid) REFERENCES public.devicetype(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: device_device_type_link device_device_type_link_device_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device_device_type_link
    ADD CONSTRAINT device_device_type_link_device_uuid_fkey FOREIGN KEY (device_uuid) REFERENCES public.device(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: device device_device_types_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_device_types_uuid_fkey FOREIGN KEY (device_types_uuid) REFERENCES public.devicetype(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: patient patient_clinic_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT patient_clinic_uuid_fkey FOREIGN KEY (clinic_uuid) REFERENCES public.clinic(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user user_clinic_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_clinic_uuid_fkey FOREIGN KEY (clinic_uuid) REFERENCES public.clinic(uuid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

