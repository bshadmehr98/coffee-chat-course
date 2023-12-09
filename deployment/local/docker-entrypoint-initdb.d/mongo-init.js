print('Start #################################################################');

db = db.getSiblingDB('coffeechat');
db.createUser(
  {
    user: 'coffeechat',
    pwd: 'coffeechat',
    roles: [{ role: 'readWrite', db: 'coffeechat' }],
  },
);
db.createCollection('delete_me');
print('END #################################################################');