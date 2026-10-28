using System;

namespace SatChara.Rules
{
    public enum MatchPhase { TowerAttack, Rebuild, RoundOver, MatchOver }
    public enum RoundResult { None, AttemptsExhausted, OpeningCatch, Rebuilt, AllOut, Timeout }

    /// <summary>
    /// Authoritative offline match state. The scene decides physical contacts and calls
    /// these commands in simulation order. No physics, AI, animation or wall-clock access.
    /// Slots 0..3 identify attackers; stones 0..6 go from biggest to smallest.
    /// </summary>
    public sealed class MatchState
    {
        private readonly int[] scores = new int[2];
        private readonly bool[] alive = new bool[4];
        private readonly int[] carried = new int[4];
        private readonly int targetScore;
        private readonly double rebuildDuration;
        private int nextAttackingTeam;

        public MatchPhase Phase { get; private set; }
        public RoundResult LastResult { get; private set; }
        public int AttackingTeam { get; private set; }
        public int ThrowsLeft { get; private set; }
        public int StackedStones { get; private set; }
        public double SecondsRemaining { get; private set; }
        public int Winner { get; private set; } = -1;
        public int LastRoundWinner { get; private set; } = -1;
        public int RoundNumber { get; private set; }

        public MatchState(int targetScore = 5, double rebuildSeconds = 45)
        {
            if (targetScore < 1) throw new ArgumentOutOfRangeException(nameof(targetScore));
            if (!Finite(rebuildSeconds) || rebuildSeconds <= 0)
                throw new ArgumentOutOfRangeException(nameof(rebuildSeconds));
            this.targetScore = targetScore;
            rebuildDuration = rebuildSeconds;
            BeginRound();
        }

        public int Score(int team) { ValidateTeam(team); return scores[team]; }
        public bool IsAlive(int slot) { ValidateSlot(slot); return alive[slot]; }
        public int CarriedStone(int slot) { ValidateSlot(slot); return carried[slot]; }

        public bool MissTower()
        {
            if (Phase != MatchPhase.TowerAttack) return false;
            if (--ThrowsLeft == 0) Resolve(-1, true, RoundResult.AttemptsExhausted);
            return true;
        }

        public bool CatchOpeningThrow()
        {
            if (Phase != MatchPhase.TowerAttack) return false;
            Resolve(-1, true, RoundResult.OpeningCatch);
            return true;
        }

        public bool ToppleTower()
        {
            if (Phase != MatchPhase.TowerAttack) return false;
            StackedStones = 0;
            SecondsRemaining = rebuildDuration;
            Phase = MatchPhase.Rebuild;
            return true;
        }

        public bool PickUpStone(int slot, int stone)
        {
            ValidateSlot(slot);
            if (stone < 0 || stone > 6) throw new ArgumentOutOfRangeException(nameof(stone));
            if (Phase != MatchPhase.Rebuild || !alive[slot] || carried[slot] != -1 || stone < StackedStones)
                return false;
            for (int i = 0; i < carried.Length; i++) if (carried[i] == stone) return false;
            carried[slot] = stone;
            return true;
        }

        public bool PlaceStone(int slot)
        {
            ValidateSlot(slot);
            if (Phase != MatchPhase.Rebuild || !alive[slot] || carried[slot] != StackedStones)
                return false;
            carried[slot] = -1;
            StackedStones++;
            if (StackedStones == 7) Resolve(AttackingTeam, false, RoundResult.Rebuilt);
            return true;
        }

        /// <summary>The scene reads CarriedStone before this call to position a dropped stone.</summary>
        public bool HitAttacker(int slot)
        {
            ValidateSlot(slot);
            if (Phase != MatchPhase.Rebuild || !alive[slot]) return false;
            alive[slot] = false;
            carried[slot] = -1;
            for (int i = 0; i < alive.Length; i++) if (alive[i]) return true;
            Resolve(1 - AttackingTeam, true, RoundResult.AllOut);
            return true;
        }

        /// <summary>Advance only with unpaused simulation time, before processing that tick's contacts.</summary>
        public void AdvanceTime(double seconds)
        {
            if (!Finite(seconds) || seconds < 0) throw new ArgumentOutOfRangeException(nameof(seconds));
            if (Phase != MatchPhase.Rebuild) return;
            SecondsRemaining = Math.Max(0, SecondsRemaining - seconds);
            if (SecondsRemaining == 0) Resolve(1 - AttackingTeam, true, RoundResult.Timeout);
        }

        public bool StartNextRound()
        {
            if (Phase != MatchPhase.RoundOver) return false;
            AttackingTeam = nextAttackingTeam;
            BeginRound();
            return true;
        }

        private void BeginRound()
        {
            RoundNumber++;
            ThrowsLeft = 3;
            StackedStones = 7;
            SecondsRemaining = rebuildDuration;
            Phase = MatchPhase.TowerAttack;
            LastResult = RoundResult.None;
            LastRoundWinner = -1;
            for (int i = 0; i < alive.Length; i++) { alive[i] = true; carried[i] = -1; }
        }

        private void Resolve(int winner, bool switchSides, RoundResult result)
        {
            if (Phase == MatchPhase.RoundOver || Phase == MatchPhase.MatchOver) return;
            LastResult = result;
            LastRoundWinner = winner;
            nextAttackingTeam = switchSides ? 1 - AttackingTeam : AttackingTeam;
            if (winner >= 0 && ++scores[winner] >= targetScore)
            {
                Winner = winner;
                Phase = MatchPhase.MatchOver;
            }
            else Phase = MatchPhase.RoundOver;
        }

        private static bool Finite(double value) => !double.IsNaN(value) && !double.IsInfinity(value);
        private static void ValidateTeam(int team)
        { if (team < 0 || team > 1) throw new ArgumentOutOfRangeException(nameof(team)); }
        private static void ValidateSlot(int slot)
        { if (slot < 0 || slot > 3) throw new ArgumentOutOfRangeException(nameof(slot)); }
    }
}
