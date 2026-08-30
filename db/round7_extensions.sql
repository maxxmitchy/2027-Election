-- Round 7 additions: focused integrity controls required for executable reconstruction.
ALTER TABLE ai_answer ADD COLUMN IF NOT EXISTS required_dependency_count integer NOT NULL DEFAULT 0 CHECK (required_dependency_count >= 0);
CREATE OR REPLACE FUNCTION enforce_published_ai_completeness() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE n integer; required_n integer;
BEGIN
  IF NEW.status='published' THEN
    SELECT required_dependency_count INTO required_n FROM ai_answer WHERE answer_id=NEW.answer_id;
    SELECT count(*) INTO n FROM ai_answer_dependency d WHERE d.answer_id=NEW.answer_id;
    IF required_n IS NULL OR n <> required_n OR n = 0 THEN
      RAISE EXCEPTION 'published AI answer dependency set incomplete';
    END IF;
  END IF;
  RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS ai_answer_completeness_guard ON ai_answer_state;
CREATE TRIGGER ai_answer_completeness_guard BEFORE UPDATE OF status ON ai_answer_state FOR EACH ROW EXECUTE FUNCTION enforce_published_ai_completeness();
