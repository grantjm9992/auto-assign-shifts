<?php

declare(strict_types=1);

class AssignShiftsService
{
    public static function assign(array $shifts, array $employees)
    {
        $shifts = self::setDifficultyIndex($shifts, $employees);
        $shifts = usort($shifts, function($a, $b) {
            /**@var Shift $a
             * @var Shift $b
             */
            return $a->difficultyIndex() < $b->difficultyIndex();
        });
    }

    public static function setDifficultyIndex(array $shifts, array $employees): array
    {
        $returnArray = [];
        foreach ($shifts as $shift) {
            $returnArray[] = self::setDifficultyIndexForShift($shift, $shifts, $employees);
        }
        return $returnArray;
    }

    public static function setDifficultyIndexForShift(Shift $shift, array $shifts, array $employees): Shift
    {
        $difficultyIndex = self::getShiftIndex($shifts, $shift->abilities()) * self::getEmployeeIndexForShift($employees, $shift->abilities());
        $shift->setDifficultyIndex($difficultyIndex);
        return $shift;
    }

    public static function getShiftIndex(array $shifts, array $abilities): float
    {
        $shiftsWithSameAbilities = 0;
        foreach ($shifts as $shift) {
            /**@var Shift $shift*/
            if ($shift->abilities() === $abilities) {
                $shiftsWithSameAbilities++;
            }
        }

        return $shiftsWithSameAbilities / count($shifts);
    }

    public static function getEmployeeIndexForShift(array $employees, array $abilities): float
    {
        $employeesThatCan = 0;
        foreach ($employees as $employee) {
            /**@var Employees $employee*/
            if ($employee->abilities() === $abilities) {
                $employeesThatCan++;
            }
        }

        if ($employeesThatCan === 0) {
            throw new Exception('No employees to cover shift');
        }

        return count($employees) / $employeesThatCan;
    }

    public static function checkIfShiftsOverlap(Shift $assignedShift, Shift $shiftToAssign): bool
    {
        if ($assignedShift->startDate()->getTimestamp() >= $shiftToAssign->endDate()->getTimestamp()) {
            return true;
        }

        if ($shiftToAssign->startDate()->getTimestamp() >= $assignedShift->endDate()->getTimestamp()) {
            return true;
        }

        return false;
    }

    public static function getEmployeesWithAbilities(array $employees, array $abilities): array
    {
        return [];
    }
}