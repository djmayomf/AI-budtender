SELECT u.id, u.name, u.email
FROM users u
WHERE EXISTS (
  SELECT 1
  FROM users u2
  WHERE u2.email = 'example@example.com'
  AND u2.date_of_birth > '1990-01-01'
);
