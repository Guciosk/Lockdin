-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    username VARCHAR NOT NULL,
    phone_number VARCHAR NOT NULL UNIQUE,
    points INT DEFAULT 0
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id INT NOT NULL REFERENCES users(id),
    description TEXT NOT NULL,
    due_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR DEFAULT 'active'
);

-- Create feed table
CREATE TABLE IF NOT EXISTS feed (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id INT NOT NULL REFERENCES users(id),
    task_id INT NOT NULL REFERENCES tasks(id),
    image_url TEXT NOT NULL,
    status VARCHAR DEFAULT 'pending',
    post_content TEXT
);

-- Create messages table (for storing incoming Twilio messages)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_sid TEXT UNIQUE NOT NULL,
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    body TEXT,
    num_media INTEGER DEFAULT 0,
    media_items JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    storage_urls JSONB DEFAULT '[]'
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_feed_user_id ON feed(user_id);
CREATE INDEX IF NOT EXISTS idx_feed_task_id ON feed(task_id);
CREATE INDEX IF NOT EXISTS idx_messages_from_number ON messages(from_number);
CREATE INDEX IF NOT EXISTS idx_messages_message_sid ON messages(message_sid);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Comment on tables
COMMENT ON TABLE users IS 'User accounts with points system';
COMMENT ON TABLE tasks IS 'Tasks assigned to users';
COMMENT ON TABLE feed IS 'Feed of completed tasks with images';
COMMENT ON TABLE messages IS 'Stores incoming messages from Twilio (SMS and WhatsApp)';

-- Create a bucket for storing media files in Supabase Storage
-- Note: This needs to be run in the Supabase SQL editor or via the Supabase API
-- CREATE BUCKET IF NOT EXISTS notes; 