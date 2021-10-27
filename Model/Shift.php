<?php

declare(strict_types=1);

class Shift
{
    public const ID = 'id';
    public const NAME = 'name';
    public const ABILITIES = 'abilities';

    private string $id;
    private string $name;
    private array $abilities;
    private DateTime $startDate;
    private DateTime $endDate;
    private float $difficultyIndex;

    public function __construct(string $id, string $name, array $abilities, DateTime $startDate, DateTime $endDate, float $difficultyIndex)
    {
        $this->id = $id;
        $this->name = $name;
        $this->abilities = $abilities;
        $this->startDate = $startDate;
        $this->endDate = $endDate;
        $this->difficultyIndex = $difficultyIndex;
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

    public function startDate(): DateTime
    {
        return $this->startDate;
    }

    public function endDate(): DateTime
    {
        return $this->endDate;
    }

    public function difficultyIndex(): float
    {
        return $this->difficultyIndex;
    }

    public function setDifficultyIndex(float $difficultyIndex): void
    {
        $this->difficultyIndex = $difficultyIndex;
    }
}