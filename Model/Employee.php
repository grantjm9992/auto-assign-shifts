<?php

declare(strict_types=1);


class Employee
{
    public const ID = 'id';
    public const NAME = 'name';
    public const ABILITIES = 'abilities';

    private string $id;
    private string $name;
    private array $abilities;
    private float $abilityIndex;

    public function __construct(string $id, string $name, array $abilities, float $abilityIndex)
    {
        $this->id = $id;
        $this->name = $name;
        $this->abilities = $abilities;
        $this->abilityIndex = $abilityIndex;
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

    public function abilityIndex(): float
    {
        return $this->abilityIndex;
    }

    public function setAbilityIndex(float $abilityIndex): void
    {
        $this->abilityIndex = $abilityIndex;
    }
}