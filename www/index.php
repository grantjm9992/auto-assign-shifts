<?php

const NAME = 'name';
const ID = 'id';

try {
    $pdo = new \PDO('mysql:host=mariadb;dbname=my_database', 'my_user', 'my_password');
    $pdo->prepare('INSERT INTO abilities(id, name) VALUES("1", "ability_1"), ("2", "ability_2")')->execute();


    $stmt = $pdo->prepare('SELECT * FROM employees');
    $stmt->execute();
    $employees = $stmt->fetchAll();

} catch (PDOException $exception) {
    echo $exception->getMessage();
}
?>