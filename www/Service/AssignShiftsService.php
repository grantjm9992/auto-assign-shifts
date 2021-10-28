<?php

declare(strict_types=1);

class AssignShiftsService
{
    public static function assign(array $shifts, array $employees)
    {
        $shifts = self::setDifficultyIndex($shifts, $employees);
        usort($shifts, function($a, $b) {
            /**@var Shift $a
             * @var Shift $b
             */
            return $a->difficultyIndex() < $b->difficultyIndex();
        });

        $employees = self::setAbilityIndex($employees, $shifts);
        usort($employees, function($a, $b) {
            /**
             *@var Employee $a
             *@var Employee $b
             */
            return $a->abilityIndex() > $b->abilityIndex();
        });

        foreach ($shifts as $shift) {
            $employee = self::getEmployeeForShift($shift, $employees);
        }
    }

    public static function getEmployeeForShift(Shift $shift, array $employees): Employee
    {
        /**@var Employee[] $employees*/
        foreach ($employees as $employee) {

        }
    }

    public static function setDifficultyIndex(array $shifts, array $employees): array
    {
        $returnArray = [];
        foreach ($shifts as $shift) {
            $returnArray[] = self::setDifficultyIndexForShift($shift, $shifts, $employees);
        }
        return $returnArray;
    }

    public static function setAbilityIndex(array $employees, array $shifts): array
    {
        $returnArray = [];
        foreach ($employees as $employee) {
            $returnArray[] = self::setAbilityIndexForEmployee($employee, $shifts, $employees);
        }
        return $returnArray;
    }

    public static function setAbilityIndexForEmployee(Employee $employee, array $shifts, array $employees): Employee
    {
        $abilityIndex = self::getEmployeeIndex($employees, $employee->abilities()) * self::getShiftIndexForEmployee($shifts, $employee->abilities());
        $employee->setAbilityIndex($abilityIndex);
        return $employee;
    }

    public static function setDifficultyIndexForShift(Shift $shift, array $shifts, array $employees): Shift
    {
        $difficultyIndex = self::getShiftIndex($shifts, $shift->abilities()) * self::getEmployeeIndexForShift($employees, $shift->abilities());
        $shift->setDifficultyIndex($difficultyIndex);
        return $shift;
    }

    public static function getEmployeeIndex(array $employees, array $abilities): float
    {
        $employeesWithSameAbilities = 0;
        foreach ($employees as $employee) {
            /**@var Employee $employee*/
            if ($employee->abilities() === $abilities) {
                $employeesWithSameAbilities++;
            }
        }

        if ($employeesWithSameAbilities === 0) {
            throw new Exception('No employees to cover shift');
        }

        return count($employees) / $employeesWithSameAbilities;
    }

    public static function getShiftIndexForEmployee(array $shifts, array $abilities): float
    {
        $shiftsEmployeeCanDo = 0;
        foreach ($shifts as $shift) {
            /**@var Shift $shift*/
            if ($shift->abilities() === $abilities) {
                $shiftsEmployeeCanDo++;
            }
        }

        return $shiftsEmployeeCanDo / count($shifts);
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
            /**@var Employee $employee*/
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