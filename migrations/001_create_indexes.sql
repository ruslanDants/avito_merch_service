CREATE INDEX idx_user_username ON "user" (username);
CREATE INDEX idx_merch_name ON merch (name);
CREATE INDEX idx_transaction_sender ON transaction (sender_id);
CREATE INDEX idx_transaction_receiver ON transaction (receiver_id);