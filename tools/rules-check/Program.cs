using System;
using SatChara.Rules;

internal static class Program
{
    private static int checks;
    private static void Check(bool condition, string message)
    {
        if (!condition) throw new Exception(message);
        checks++;
    }

    private static void Rebuild(MatchState match, int slot = 0)
    {
        Check(match.ToppleTower(), "Tower should topple once during opening attack");
        for (int stone = 0; stone < 7; stone++)
        {
            Check(match.PickUpStone(slot, stone), "Required stone must be available");
            Check(match.PlaceStone(slot), "Required stone must place");
        }
    }

    public static void Main()
    {
        var missed = new MatchState();
        Check(!missed.PlaceStone(0), "Cannot place before tower falls");
        for (int i = 0; i < 3; i++) Check(missed.MissTower(), "Three misses accepted");
        Check(!missed.MissTower() && missed.Score(0) == 0 && missed.Score(1) == 0,
            "Exhaustion cannot award points or process duplicate misses");
        Check(missed.StartNextRound() && missed.AttackingTeam == 1 && missed.ThrowsLeft == 3,
            "Misses switch attack and reset attempts");
        Check(missed.CatchOpeningThrow() && missed.StartNextRound() && missed.AttackingTeam == 0,
            "Opening catch changes sides without points");

        var carrying = new MatchState();
        carrying.ToppleTower();
        Check(carrying.PickUpStone(0, 1) && !carrying.PlaceStone(0), "Smaller stone cannot precede largest");
        Check(!carrying.PickUpStone(1, 1), "Stone cannot have two owners");
        Check(!carrying.PickUpStone(0, 0), "Player cannot carry two stones");
        Check(carrying.HitAttacker(0) && carrying.CarriedStone(0) == -1, "Hit drops carried stone");
        Check(!carrying.PlaceStone(0) && !carrying.PickUpStone(0, 0), "Out player cannot rebuild");
        Check(carrying.PickUpStone(1, 1), "Dropped stone becomes available");
        carrying.HitAttacker(1); carrying.HitAttacker(2); carrying.HitAttacker(3);
        Check(carrying.Score(1) == 1 && carrying.LastResult == RoundResult.AllOut, "All out scores for defense");
        Check(!carrying.HitAttacker(3) && carrying.Score(1) == 1, "Duplicate hit cannot duplicate score");
        carrying.StartNextRound();
        Check(carrying.IsAlive(0) && carrying.CarriedStone(1) == -1 && carrying.StackedStones == 7,
            "New round restores players, tower and inventory");

        var rebuilt = new MatchState(2);
        Rebuild(rebuilt);
        Check(rebuilt.Score(0) == 1 && rebuilt.LastResult == RoundResult.Rebuilt, "Seven stones score once");
        Check(!rebuilt.PlaceStone(0), "Resolved round rejects placement");
        rebuilt.AdvanceTime(100);
        Check(rebuilt.Score(1) == 0 && rebuilt.StartNextRound() && rebuilt.AttackingTeam == 0,
            "Rebuilders retain attack and resolved timer cannot award defense");
        Rebuild(rebuilt);
        Check(rebuilt.Phase == MatchPhase.MatchOver && rebuilt.Winner == 0 && !rebuilt.StartNextRound(),
            "Target score ends match and blocks restart");

        var timeout = new MatchState();
        timeout.ToppleTower();
        timeout.AdvanceTime(44.9);
        Check(timeout.Phase == MatchPhase.Rebuild, "Clock cannot expire early");
        timeout.AdvanceTime(0.2);
        Check(timeout.SecondsRemaining == 0 && timeout.Score(1) == 1, "Timeout clamps clock and scores");
        timeout.AdvanceTime(100);
        Check(!timeout.PlaceStone(0) && timeout.Score(1) == 1 && !timeout.ToppleTower(),
            "Timeout locks later contacts and duplicate outcomes");
        bool rejected = false;
        try { timeout.AdvanceTime(double.NaN); } catch (ArgumentOutOfRangeException) { rejected = true; }
        Check(rejected, "Invalid time must be rejected");
        Console.WriteLine($"PASS: {checks} match-rule assertions. No Unity/physics/device coverage claimed.");
    }
}
