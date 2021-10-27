<?php

declare(strict_types=1);


class Employees
{
    public const ID = 'id';
    public const NAME = 'name';
    public const ABILITIES = 'abilities';

    private string $id;
    private string $name;
    private array $abilities;

    public function __construct(string $id, string $name, array $abilities)
    {
        $this->id = $id;
        $this->name = $name;
        $this->abilities = $abilities;
    }

    public function id(): string
    {
        return $this->id;
    }

    public function name(): string
    {
        return $this->name;
    }

    public function abilities(): array
    {
        return $this->abilities;
    }
}