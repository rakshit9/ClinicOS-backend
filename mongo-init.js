// MongoDB initialization script
db = db.getSiblingDB('clinic_auth');

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'password_hash', 'name', 'role', 'verified', 'created_at', 'updated_at'],
      properties: {
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
          description: 'Email must be a valid email address'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Password hash is required'
        },
        name: {
          bsonType: 'string',
          minLength: 1,
          description: 'Name is required and must be at least 1 character'
        },
        role: {
          enum: ['doctor', 'admin'],
          description: 'Role must be either doctor or admin'
        },
        verified: {
          bsonType: 'bool',
          description: 'Verified must be a boolean'
        },
        created_at: {
          bsonType: 'date',
          description: 'Created at must be a date'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Updated at must be a date'
        }
      }
    }
  }
});

db.createCollection('refresh_tokens', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'jti', 'token_hash', 'revoked', 'expires_at', 'created_at'],
      properties: {
        user_id: {
          bsonType: 'string',
          description: 'User ID is required'
        },
        jti: {
          bsonType: 'string',
          description: 'JWT ID is required'
        },
        token_hash: {
          bsonType: 'string',
          description: 'Token hash is required'
        },
        user_agent: {
          bsonType: 'string',
          description: 'User agent must be a string'
        },
        ip_address: {
          bsonType: 'string',
          description: 'IP address must be a string'
        },
        revoked: {
          bsonType: 'bool',
          description: 'Revoked must be a boolean'
        },
        expires_at: {
          bsonType: 'date',
          description: 'Expires at must be a date'
        },
        created_at: {
          bsonType: 'date',
          description: 'Created at must be a date'
        }
      }
    }
  }
});

db.createCollection('reset_tokens', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'token_hash', 'expires_at', 'created_at'],
      properties: {
        user_id: {
          bsonType: 'string',
          description: 'User ID is required'
        },
        token_hash: {
          bsonType: 'string',
          description: 'Token hash is required'
        },
        expires_at: {
          bsonType: 'date',
          description: 'Expires at must be a date'
        },
        created_at: {
          bsonType: 'date',
          description: 'Created at must be a date'
        }
      }
    }
  }
});

print('✅ Database and collections initialized successfully');
