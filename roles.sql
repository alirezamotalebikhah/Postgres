--
-- PostgreSQL database cluster dump
--

\restrict 5WwtdUohZYzp0cxTkmEDoLKqtmj60yEVZfmfRUBaqwjDGEPWvUdFTidgvMz6Qw3

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE myuser;
ALTER ROLE myuser WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:29yCsB8Djv0QUlrIAHmsuw==$ECfxBfCixmrvCPVFCNx1w4gdA72gr4uYuf8+GNhLHZY=:Va0M8HlAAd8J0lwebNOOaOxjyVbT40Gh7IAle+2SqEU=';

--
-- User Configurations
--








\unrestrict 5WwtdUohZYzp0cxTkmEDoLKqtmj60yEVZfmfRUBaqwjDGEPWvUdFTidgvMz6Qw3

--
-- PostgreSQL database cluster dump complete
--

