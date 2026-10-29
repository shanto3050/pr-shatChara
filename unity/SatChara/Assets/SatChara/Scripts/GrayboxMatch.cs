using System;
using SatChara.Rules;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;

namespace SatChara
{
    /// <summary>M1 playable simulation. Primitives are deliberate development art.</summary>
    public sealed class GrayboxMatch : MonoBehaviour
    {
        [SerializeField] private Material materialTemplate;
        [SerializeField] private GameObject villageCharacter;
        [SerializeField] private Material villageGround;
        [SerializeField] private Mesh villageStone;
        private readonly VillageAvatar[] avatars = new VillageAvatar[8];
        private readonly Transform[] teamMarkers = new Transform[8];
        public bool AutomatedPlayer;
        public MatchState State { get; private set; }
        public int Topples { get; private set; }
        public int Hits { get; private set; }
        public int Placements { get; private set; }
        public int CompletedRounds { get; private set; }
        public Vector3 HumanPosition => players[HumanIndex()].position;

        private readonly Transform[] players = new Transform[8];
        private readonly Renderer[] bodies = new Renderer[8];
        private readonly TextMesh[] names = new TextMesh[8];
        private readonly float[] windup = new float[8];
        private readonly float[] duck = new float[8];
        private readonly float[] dodge = new float[8];
        private readonly float[] dodgeCooldown = new float[8];
        private readonly Vector3[] dodgeDirection = new Vector3[8];
        private readonly Transform[] stones = new Transform[7];
        private readonly TextMesh[] stoneLabels = new TextMesh[7];
        private readonly int[] reserved = new int[7];
        private Material blue, red, selected, gray, gold, ballMat;
        private Transform ball;
        private Vector3 ballVelocity, aimDirection = Vector3.forward;
        private int holder = -1, throwingTeam, thrower, humanSlot;
        private bool flying, initialized, paused, suspended, closeCamera;
        private float flightTime, openingTime, transitionTime, cooldown;
        private MatchPhase lastPhase;
        private Camera view;
        private LineRenderer aimLine;
        private Text scoreboard, instructions;
        private Button dodgeButton, duckButton, passButton;
        private TouchStick movement, aiming;
        private RectTransform safeArea;
        private Rect lastSafeArea;
        private Font font;
        private readonly string[] labels = { "YOU", "B2", "B3", "B4", "R1", "R2", "R3", "R4" };

        public void SetMaterial(Material value) => materialTemplate = value;
        public void SetVillageArt(GameObject character, Material ground, Mesh stone)
        { villageCharacter = character; villageGround = ground; villageStone = stone; }
        private void Start() => Initialize();

        public void Initialize()
        {
            if (initialized) return;
            initialized = true;
            if (villageCharacter) closeCamera = true;
            Application.targetFrameRate = 30;
            font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            blue = MakeMaterial(new Color(.12f, .38f, .78f));
            red = MakeMaterial(new Color(.8f, .24f, .14f));
            selected = MakeMaterial(new Color(.2f, .72f, 1));
            gray = MakeMaterial(new Color(.62f, .6f, .55f));
            gold = MakeMaterial(new Color(1, .73f, .08f));
            ballMat = MakeMaterial(new Color(1, .3f, .04f));
            if (!villageCharacter) Shape("Courtyard", PrimitiveType.Plane, Vector3.zero, new Vector3(2.4f, 1, 3), MakeMaterial(new Color(.32f, .38f, .23f)));
            Shape("Tower base", PrimitiveType.Cylinder, new Vector3(0, .01f, 0), new Vector3(villageCharacter ? .9f : 1.8f, .01f, villageCharacter ? .9f : 1.8f), gray);
            if (villageGround) gray.SetTexture("_BaseMap", villageGround.GetTexture("_BaseMap"));
            for (int i = 0; i < 8; i++)
            {
                players[i] = Shape(labels[i], PrimitiveType.Capsule, Vector3.zero, new Vector3(.7f, .9f, .7f), i < 4 ? blue : red);
                bodies[i] = players[i].GetComponent<Renderer>();
                if (villageCharacter)
                {
                    bodies[i].enabled = false; players[i].localScale = Vector3.one;
                    var model = Instantiate(villageCharacter, players[i]);
                    model.transform.localPosition = new Vector3(0, -.9f, 0);
                    avatars[i] = model.GetComponent<VillageAvatar>();
                    teamMarkers[i] = Shape("Team marker", PrimitiveType.Cylinder, Vector3.zero, new Vector3(.6f, .008f, .6f), i < 4 ? blue : red);
                }
                names[i] = WorldLabel(labels[i]);
            }
            for (int i = 0; i < 7; i++)
            {
                stones[i] = Shape("Stone " + (i + 1), PrimitiveType.Cylinder, Vector3.zero, new Vector3(1.2f - i * .12f, .10f, 1.2f - i * .12f), gray);
                if (villageStone)
                {
                    stones[i].GetComponent<MeshFilter>().sharedMesh = villageStone;
                    stones[i].localScale = new Vector3(.54f - i * .045f, .045f, .54f - i * .045f);
                }
                stoneLabels[i] = WorldLabel((i + 1).ToString());
            }
            ball = Shape("Ball", PrimitiveType.Sphere, Vector3.zero, Vector3.one * .38f, ballMat);
            if (villageCharacter) ball.localScale = Vector3.one * .18f;
            view = Camera.main;
            aimLine = new GameObject("Throw direction").AddComponent<LineRenderer>();
            aimLine.sharedMaterial = gold; aimLine.startWidth = .07f; aimLine.endWidth = .02f; aimLine.positionCount = 2;
            BuildUI();
            NewMatch();
        }

        public void NewMatch()
        {
            State = new MatchState();
            Topples = Hits = Placements = CompletedRounds = 0;
            paused = false; humanSlot = 0;
            SetupRound();
        }

        private void SetupRound()
        {
            int att = State.AttackingTeam * 4;
            for (int i = 0; i < 8; i++)
            {
                bool attack = i / 4 == State.AttackingTeam;
                players[i].position = attack ? new Vector3((i % 4 - 1.5f) * 2.3f, .9f, -10)
                    : new Vector3((i % 4 - 1.5f) * 3, .9f, 5 + (i % 2) * 3);
                players[i].gameObject.SetActive(true);
                windup[i] = duck[i] = dodge[i] = dodgeCooldown[i] = 0;
            }
            players[att].position = new Vector3(0, .9f, -10);
            for (int i = 0; i < 7; i++) StackStone(i);
            humanSlot = 0; holder = att; flying = false; openingTime = transitionTime = cooldown = 0;
            aimDirection = Vector3.forward;
            lastPhase = State.Phase;
            movement?.ResetInput(); aiming?.ResetInput();
            Debug.Log($"SAT_CHARA_ROUND_START: round={State.RoundNumber}, attacking={State.AttackingTeam}");
        }

        private void Update()
        {
            if (!initialized) return;
            ApplySafeArea();
            if (Keyboard.current != null)
            {
                if (Keyboard.current.spaceKey.wasPressedThisFrame) ThrowHuman();
                if (Keyboard.current.cKey.wasPressedThisFrame) DuckHuman();
                if (Keyboard.current.leftShiftKey.wasPressedThisFrame) DodgeHuman();
            }
            UpdatePresentation();
        }
        private void FixedUpdate() { if (initialized) Simulate(Time.fixedDeltaTime); }

        // Public deterministic-time stepping supports headless integration checks.
        public void Simulate(float dt)
        {
            if (!initialized || paused || suspended || dt <= 0) return;
            cooldown -= dt;
            if (State.Phase == MatchPhase.RoundOver)
            {
                transitionTime += dt;
                if (transitionTime > 2.5f && State.StartNextRound()) SetupRound();
                return;
            }
            if (State.Phase == MatchPhase.MatchOver) return;
            State.AdvanceTime(dt); // Deadline wins before any contact this tick.
            if (State.Phase != MatchPhase.Rebuild && State.Phase != MatchPhase.TowerAttack) { ObservePhase(); return; }
            for (int i = 0; i < 7; i++) reserved[i] = -1;
            for (int i = 0; i < 8; i++)
            {
                duck[i] = Mathf.Max(0, duck[i] - dt); dodge[i] = Mathf.Max(0, dodge[i] - dt);
                dodgeCooldown[i] = Mathf.Max(0, dodgeCooldown[i] - dt);
                if (!Alive(i)) continue;
                bool human = i == HumanIndex() && !AutomatedPlayer;
                if (human) MoveHuman(i, dt); else MoveBot(i, dt);
                if (State.Phase == MatchPhase.Rebuild && i / 4 == State.AttackingTeam) Interact(i % 4, dt);
            }
            if (State.Phase == MatchPhase.TowerAttack && holder >= 0 && (holder / 4 == 1 || AutomatedPlayer))
            {
                openingTime += dt;
                if (openingTime > 1.4f) ReleaseBall((Vector3.zero - Flat(players[holder].position)).normalized, 18);
            }
            StepBall(dt);
            ObservePhase();
        }

        private void ObservePhase()
        {
            if (State.Phase == lastPhase) return;
            if (State.Phase == MatchPhase.RoundOver || State.Phase == MatchPhase.MatchOver)
            {
                CompletedRounds++;
                Debug.Log($"SAT_CHARA_ROUND_END: round={State.RoundNumber}, result={State.LastResult}, score={State.Score(0)}-{State.Score(1)}");
                transitionTime = 0;
            }
            lastPhase = State.Phase;
        }

        private void MoveHuman(int i, float dt)
        {
            Vector2 value = movement.Value;
            if (Keyboard.current != null)
                value += new Vector2((Keyboard.current.dKey.isPressed ? 1 : 0) - (Keyboard.current.aKey.isPressed ? 1 : 0),
                    (Keyboard.current.wKey.isPressed ? 1 : 0) - (Keyboard.current.sKey.isPressed ? 1 : 0));
            if (aiming.Held && aiming.Value.sqrMagnitude > .04f)
                aimDirection = new Vector3(aiming.Value.x, 0, aiming.Value.y).normalized;
            if (holder == i || duck[i] > 0 || (State.Phase == MatchPhase.TowerAttack && i / 4 == State.AttackingTeam)) return;
            Vector3 direction = dodge[i] > 0 ? dodgeDirection[i] * 2.3f : new Vector3(value.x, 0, value.y);
            Move(i, direction, dt);
            if (State.Phase == MatchPhase.TowerAttack)
            { var p = players[i].position; p.z = Mathf.Max(1.8f, p.z); players[i].position = p; }
        }

        private void MoveBot(int i, float dt)
        {
            if (State.Phase != MatchPhase.Rebuild) return;
            if (i / 4 == State.AttackingTeam)
            {
                int carry = State.CarriedStone(i % 4);
                Vector3 target;
                if (carry >= 0) target = carry == State.StackedStones ? Vector3.zero : new Vector3(Mathf.Cos(i * 2) * 2, 0, Mathf.Sin(i * 2) * 2);
                else
                {
                    int best = -1; float cost = float.MaxValue;
                    for (int s = State.StackedStones; s < 7; s++)
                    {
                        if (StoneHeld(s) || reserved[s] >= 0) continue;
                        float c = Vector3.Distance(Flat(players[i].position), Flat(stones[s].position)) + (s - State.StackedStones) * 4;
                        if (c < cost) { cost = c; best = s; }
                    }
                    if (best < 0) return;
                    reserved[best] = i; target = stones[best].position;
                }
                Vector3 delta = Flat(target - players[i].position);
                if (delta.magnitude > .5f) Move(i, delta.normalized * .85f, dt);
                // Readable lateral avoidance, rather than probabilistic invulnerability.
                if (flying && throwingTeam != State.AttackingTeam && Vector3.Distance(players[i].position, ball.position) < 3 && dodgeCooldown[i] <= 0)
                { dodgeDirection[i] = Vector3.Cross(Vector3.up, ballVelocity).normalized; dodge[i] = .2f; dodgeCooldown[i] = 2; }
                if (dodge[i] > 0) Move(i, dodgeDirection[i], dt);
            }
            else if (holder == i)
            {
                windup[i] += dt;
                if (windup[i] >= 1.6f)
                {
                    int target = NearestAttacker(players[i].position);
                    if (target >= 0) ReleaseBall(Flat(players[target].position - players[i].position).normalized, 15);
                }
            }
            else if (holder < 0)
            {
                int fetcher = NearestDefender(ball.position);
                Vector3 target = fetcher == i ? ball.position : new Vector3((i % 4 - 1.5f) * 3, 0, 3);
                var delta = Flat(target - players[i].position);
                if (delta.magnitude > .55f) Move(i, delta.normalized * .9f, dt);
            }
        }

        private void Move(int i, Vector3 direction, float dt)
        {
            if (direction.sqrMagnitude > 1 && dodge[i] <= 0) direction.Normalize();
            float speed = State.AttackingTeam == i / 4 && State.CarriedStone(i % 4) >= 0 ? 3.4f : 4.1f;
            Vector3 p = players[i].position + direction * speed * dt;
            players[i].position = new Vector3(Mathf.Clamp(p.x, -11, 11), .9f, Mathf.Clamp(p.z, -13, 13));
        }

        private void Interact(int slot, float dt)
        {
            if (!State.IsAlive(slot) || State.Phase != MatchPhase.Rebuild) return;
            var p = players[State.AttackingTeam * 4 + slot].position;
            int carried = State.CarriedStone(slot);
            if (carried < 0)
            {
                for (int s = State.StackedStones; s < 7; s++)
                    if (!StoneHeld(s) && Vector3.Distance(Flat(p), Flat(stones[s].position)) < .85f && State.PickUpStone(slot, s))
                    { Debug.Log($"SAT_CHARA_PICKUP: slot={slot}, stone={s}"); break; }
            }
            else
            {
                stones[carried].position = villageCharacter ? p + Vector3.up * .2f + avatars[State.AttackingTeam * 4 + slot].transform.forward * .35f : p + Vector3.up * .5f;
                if (Flat(p).magnitude < 1.1f && carried == State.StackedStones && State.PlaceStone(slot))
                { StackStone(carried); Placements++; Debug.Log($"SAT_CHARA_PLACE: stone={carried}"); }
            }
        }

        private void ReleaseBall(Vector3 direction, float speed)
        {
            if (holder < 0 || paused || suspended || cooldown > 0) return;
            if (State.Phase != MatchPhase.TowerAttack && State.Phase != MatchPhase.Rebuild) return;
            if (direction.sqrMagnitude < .01f) return;
            thrower = holder; throwingTeam = holder / 4;
            ball.position = villageCharacter ? avatars[holder].HandPosition + direction * .2f : players[holder].position + Vector3.up * .2f + direction * .7f;
            float vertical = 1.8f;
            if (villageCharacter && State.Phase == MatchPhase.TowerAttack)
            { float travel = Mathf.Max(.1f, Flat(ball.position).magnitude / speed); vertical = (.18f - ball.position.y + 4.9f * travel * travel) / travel; }
            ballVelocity = direction * speed + Vector3.up * vertical;
            if (villageCharacter) avatars[holder].Throw();
            windup[holder] = 0; holder = -1; flying = true; flightTime = 0; cooldown = .4f;
            Debug.Log($"SAT_CHARA_THROW: player={thrower}, phase={State.Phase}");
        }

        public void ThrowHuman()
        {
            if (holder == HumanIndex()) ReleaseBall(aimDirection, State.Phase == MatchPhase.TowerAttack ? 18 : 16);
        }
        private void PassHuman()
        {
            int h = HumanIndex(); if (holder != h || State.Phase != MatchPhase.Rebuild || State.AttackingTeam == 0) return;
            int target = (h % 4 + 1) % 4;
            ReleaseBall(Flat(players[target].position - players[h].position).normalized, 11);
        }
        private void DodgeHuman()
        {
            int h = HumanIndex(); if (paused || State.Phase != MatchPhase.Rebuild || State.AttackingTeam != 0 || dodgeCooldown[h] > 0) return;
            Vector2 v = movement.Value;
            dodgeDirection[h] = v.sqrMagnitude > .04f ? new Vector3(v.x, 0, v.y).normalized : Vector3.right;
            dodge[h] = .22f; dodgeCooldown[h] = 1.8f;
        }
        private void DuckHuman()
        {
            int h = HumanIndex(); if (paused || State.Phase != MatchPhase.Rebuild || State.AttackingTeam != 0 || dodgeCooldown[h] > 0) return;
            duck[h] = .55f; dodgeCooldown[h] = 1.5f;
        }

        private void StepBall(float dt)
        {
            if (holder >= 0) { ball.position = villageCharacter ? avatars[holder].HandPosition : players[holder].position + new Vector3(.5f, .2f, 0); return; }
            Vector3 from = ball.position;
            ballVelocity.y -= 9.8f * dt;
            ball.position += ballVelocity * dt; flightTime += dt;
            var p = ball.position;
            if (p.y < .19f) { p.y = .19f; ballVelocity.y = Mathf.Abs(ballVelocity.y) * .38f; ballVelocity.x *= .85f; ballVelocity.z *= .85f; }
            if (Mathf.Abs(p.x) > 11.5f) { p.x = Mathf.Clamp(p.x, -11.5f, 11.5f); ballVelocity.x *= -.45f; }
            if (Mathf.Abs(p.z) > 13.5f) { p.z = Mathf.Clamp(p.z, -13.5f, 13.5f); ballVelocity.z *= -.45f; }
            ball.position = p;
            ballVelocity.x *= 1 - dt * .25f; ballVelocity.z *= 1 - dt * .25f;
            float speed = Flat(ballVelocity).magnitude;
            int contactPlayer = -1;
            float firstContact = float.PositiveInfinity, closestEnd = float.PositiveInfinity;
            for (int i = 0; i < 8; i++)
            {
                if (!Alive(i) || (i == thrower && flightTime < .3f)) continue;
                bool defender = i / 4 != State.AttackingTeam;
                bool eligible = State.Phase == MatchPhase.TowerAttack ? defender && flying
                    : State.Phase == MatchPhase.Rebuild && (defender ? throwingTeam == i / 4 || !flying : throwingTeam != State.AttackingTeam && flying && speed > 5);
                if (!eligible) continue;
                float centre = duck[i] > 0 ? .4f : .9f;
                float hit = SweepFraction(from, p, Flat(players[i].position) + Vector3.up * centre, .65f);
                float endDistance = Vector3.Distance(players[i].position, p);
                if (defender && !flying && endDistance < 1.15f) hit = Mathf.Min(hit, 1);
                if (hit < firstContact || (!float.IsPositiveInfinity(hit) && Mathf.Approximately(hit, firstContact) && endDistance < closestEnd))
                { firstContact = hit; closestEnd = endDistance; contactPlayer = i; }
            }
            float towerContact = State.Phase == MatchPhase.TowerAttack && flying
                ? SweepFraction(from, p, new Vector3(0, villageCharacter ? .18f : .7f, 0), villageCharacter ? .35f : .95f) : float.PositiveInfinity;
            if (!float.IsPositiveInfinity(towerContact) && towerContact <= firstContact)
            {
                ball.position = Vector3.Lerp(from, p, towerContact);
                State.ToppleTower(); Topples++;
                for (int s = 0; s < 7; s++)
                {
                    float angle = s * Mathf.PI * 2 / 7 + State.RoundNumber * .3f;
                    stones[s].position = new Vector3(Mathf.Cos(angle) * (3.2f + s * .18f), villageCharacter ? .035f : .14f, Mathf.Sin(angle) * (3.2f + s * .18f));
                }
                ballVelocity *= .5f;
                Debug.Log("SAT_CHARA_TOPPLE");
                return;
            }
            if (contactPlayer >= 0)
            {
                int i = contactPlayer;
                ball.position = Vector3.Lerp(from, p, firstContact);
                if (State.Phase == MatchPhase.TowerAttack)
                {
                    State.CatchOpeningThrow(); holder = i; flying = false;
                    return;
                }
                if (i / 4 != State.AttackingTeam)
                {
                    holder = i; flying = false; ballVelocity = Vector3.zero; windup[i] = 0;
                }
                else
                {
                    int stone = State.CarriedStone(i % 4);
                    if (stone >= 0) stones[stone].position = Flat(players[i].position) + Vector3.up * (villageCharacter ? .035f : .14f);
                    if (State.HitAttacker(i % 4)) { Hits++; Debug.Log($"SAT_CHARA_HIT: slot={i % 4}"); }
                    ballVelocity *= .25f; flying = false;
                }
            }
            if (speed < 5.5f || flightTime > 3) flying = false;
            if (State.Phase == MatchPhase.TowerAttack && !flying)
            {
                State.MissTower();
                if (State.Phase == MatchPhase.TowerAttack)
                { holder = State.AttackingTeam * 4; openingTime = 0; ballVelocity = Vector3.zero; }
            }
        }

        private int HumanIndex()
        {
            if (State.AttackingTeam == 0 && !State.IsAlive(humanSlot))
                for (int i = 0; i < 4; i++) if (State.IsAlive(i)) { humanSlot = i; break; }
            return State.AttackingTeam == 0 ? humanSlot : 0;
        }
        private bool Alive(int i) => i / 4 != State.AttackingTeam || State.IsAlive(i % 4);
        private bool StoneHeld(int stone)
        { for (int i = 0; i < 4; i++) if (State.CarriedStone(i) == stone) return true; return false; }
        private int NearestAttacker(Vector3 p)
        {
            int best = -1; float distance = float.MaxValue;
            for (int i = State.AttackingTeam * 4; i < State.AttackingTeam * 4 + 4; i++)
                if (Alive(i) && Vector3.Distance(players[i].position, p) < distance) { best = i; distance = Vector3.Distance(players[i].position, p); }
            return best;
        }
        private int NearestDefender(Vector3 p)
        {
            int best = -1; float distance = float.MaxValue;
            for (int i = (1 - State.AttackingTeam) * 4; i < (1 - State.AttackingTeam) * 4 + 4; i++)
                if (Vector3.Distance(players[i].position, p) < distance) { best = i; distance = Vector3.Distance(players[i].position, p); }
            return best;
        }
        private static Vector3 Flat(Vector3 p) => new Vector3(p.x, 0, p.z);
        public static float SweepFraction(Vector3 a, Vector3 b, Vector3 centre, float radius)
        {
            Vector3 offset = a - centre, direction = b - a;
            float c = offset.sqrMagnitude - radius * radius;
            if (c <= 0) return 0;
            float length = direction.sqrMagnitude;
            if (length < .000001f) return float.PositiveInfinity;
            float projection = Vector3.Dot(offset, direction);
            float discriminant = projection * projection - length * c;
            if (discriminant < 0) return float.PositiveInfinity;
            float t = (-projection - Mathf.Sqrt(discriminant)) / length;
            return t >= 0 && t <= 1 ? t : float.PositiveInfinity;
        }
        private void StackStone(int s) => stones[s].position = new Vector3(0, villageCharacter ? .035f + s * .045f : .15f + s * .2f, 0);

        private void UpdatePresentation()
        {
            int h = HumanIndex();
            for (int i = 0; i < 8; i++)
            {
                players[i].gameObject.SetActive(Alive(i)); names[i].gameObject.SetActive(Alive(i));
                bodies[i].sharedMaterial = i == h ? selected : i < 4 ? blue : red;
                var position = players[i].position;
                players[i].position = new Vector3(position.x, !villageCharacter && duck[i] > 0 ? .4f : .9f, position.z);
                players[i].localScale = villageCharacter ? Vector3.one : new Vector3(.7f, duck[i] > 0 ? .4f : .9f, .7f);
                if (villageCharacter)
                {
                    Vector3 facing = Vector3.forward;
                    if (holder == i) facing = i == h ? aimDirection : Flat(players[Mathf.Max(0, NearestAttacker(players[i].position))].position - position);
                    else if (State.Phase == MatchPhase.Rebuild) facing = Flat((i / 4 == State.AttackingTeam && State.CarriedStone(i % 4) >= 0 ? Vector3.zero : ball.position) - position);
                    avatars[i].Drive(facing, holder == i, i / 4 == State.AttackingTeam && State.CarriedStone(i % 4) >= 0, duck[i] > 0, i == h && aiming.Held ? aiming.Value.magnitude : windup[i], paused || suspended);
                    teamMarkers[i].gameObject.SetActive(Alive(i)); teamMarkers[i].position = Flat(position) + Vector3.up * .014f;
                }
                names[i].text = (i == h ? "YOU" : labels[i]) + (holder == i ? (windup[i] > .7f ? " !" : " *") : "");
                names[i].transform.position = Flat(players[i].position) + Vector3.up * 2.2f;
                names[i].transform.rotation = view.transform.rotation;
            }
            for (int s = 0; s < 7; s++)
            {
                stones[s].GetComponent<Renderer>().sharedMaterial = State.Phase == MatchPhase.Rebuild && s == State.StackedStones ? gold : gray;
                stoneLabels[s].gameObject.SetActive(State.Phase == MatchPhase.Rebuild && s >= State.StackedStones);
                stoneLabels[s].transform.position = stones[s].position + Vector3.up * .5f;
                stoneLabels[s].transform.rotation = view.transform.rotation;
            }
            Vector3 target = closeCamera ? Vector3.Lerp(new Vector3(0, 0, 3), Flat(players[h].position), .4f) : new Vector3(0, 0, 3);
            view.transform.position = target + (closeCamera ? new Vector3(0, 22, -16) : new Vector3(0, 29, -19));
            view.transform.LookAt(target);
            view.orthographic = true; view.orthographicSize = closeCamera ? 12 : 18.5f;
            if (villageCharacter)
            {
                target = closeCamera ? Vector3.Lerp(new Vector3(0, .7f, 0), Flat(players[h].position) + Vector3.up * .7f, .65f) : new Vector3(0, .7f, 1);
                view.orthographic = false; view.fieldOfView = closeCamera ? 58 : 63;
                view.transform.position = target + (closeCamera ? new Vector3(4, 6.5f, -12) : new Vector3(0, 15, -19));
                view.transform.LookAt(target);
            }
            aimLine.enabled = holder == h && !paused && State.Phase != MatchPhase.MatchOver;
            aimLine.SetPosition(0, players[h].position); aimLine.SetPosition(1, players[h].position + aimDirection * 6);
            scoreboard.text = $"BLUE {State.Score(0)}    :    {State.Score(1)} RED     |     ROUND {State.RoundNumber}";
            string phase = State.Phase == MatchPhase.TowerAttack ? $"{(State.AttackingTeam == 0 ? "ATTACK" : "DEFEND")}  ·  {State.ThrowsLeft} throws"
                : State.Phase == MatchPhase.Rebuild ? $"{(State.AttackingTeam == 0 ? "REBUILD" : "DEFEND")}  ·  {Mathf.CeilToInt((float)State.SecondsRemaining)}s  ·  {State.StackedStones}/7 stones"
                : State.Phase == MatchPhase.MatchOver ? $"{(State.Winner == 0 ? "BLUE WINS" : "RED WINS")} — tap New match" : $"{State.LastResult} — next round";
            instructions.text = paused ? "PAUSED" : phase + (villageCharacter ? "\nDrag AIM and release to throw · Move with the left stick" : "\nLeft stick: move   ·   Right stick: aim, release to throw   ·   Collect/place nearby automatically");
            dodgeButton.interactable = duckButton.interactable = !paused && State.Phase == MatchPhase.Rebuild && State.AttackingTeam == 0 && dodgeCooldown[h] <= 0;
            passButton.interactable = !paused && holder == h && State.Phase == MatchPhase.Rebuild && State.AttackingTeam == 1;
        }

        private void BuildUI()
        {
            var canvas = new GameObject("Match UI", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvas.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvas.GetComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 720); scaler.matchWidthOrHeight = 1;
            safeArea = new GameObject("Safe area", typeof(RectTransform)).GetComponent<RectTransform>(); safeArea.SetParent(canvas.transform, false);
            ApplySafeArea();
            var events = new GameObject("Event System", typeof(EventSystem), typeof(InputSystemUIInputModule));
            events.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
            if (villageCharacter)
            {
                var header = UIBox("Score backdrop", safeArea, new Vector2(.5f,1), new Vector2(0,-59), new Vector2(1000,112), new Color(.035f,.055f,.07f,.88f));
                header.GetComponent<Image>().raycastTarget = false;
            }
            scoreboard = UIText("Score", safeArea, new Vector2(.5f, 1), new Vector2(0, -26), new Vector2(720, 42), 26);
            instructions = UIText("Phase", safeArea, new Vector2(.5f, 1), new Vector2(0, -78), new Vector2(1000, 72), 20);
            movement = Stick("MOVE", new Vector2(0, 0), new Vector2(135, 125));
            movement.Released = () => Debug.Log($"SAT_CHARA_MOVE_INPUT: position={HumanPosition}");
            aiming = Stick("AIM / RELEASE", new Vector2(1, 0), new Vector2(-135, 125)); aiming.Released = ThrowHuman;
            dodgeButton = UIButton("Dodge", new Vector2(1, 0), new Vector2(-360, 82), DodgeHuman);
            duckButton = UIButton("Duck", new Vector2(1, 0), new Vector2(-360, 145), DuckHuman);
            passButton = UIButton("Pass", new Vector2(1, 0), new Vector2(-360, 208), PassHuman);
            var quality = GetComponent<MobileVisualQuality>();
            if (quality)
            {
                Button qualityButton = null;
                qualityButton = UIButton(quality.Label, new Vector2(0,1),new Vector2(88,-95),()=>
                { quality.Next(); qualityButton.GetComponentInChildren<Text>().text=quality.Label; });
            }
            UIButton("Camera", new Vector2(0, 1), new Vector2(88, -32), () => closeCamera = !closeCamera);
            UIButton("Pause", new Vector2(1, 1), new Vector2(-85, -32), () =>
            {
                paused = !paused; movement.ResetInput(); aiming.ResetInput();
                Debug.Log($"SAT_CHARA_PAUSE: paused={paused}, remaining={State.SecondsRemaining:F2}");
            });
            UIButton("New match", new Vector2(1, 1), new Vector2(-85, -95), NewMatch);
        }
        private TouchStick Stick(string name, Vector2 anchor, Vector2 position)
        {
            var root = UIBox(name, safeArea, anchor, position, new Vector2(180, 180), new Color(.08f, .13f, .17f, .7f));
            var stick = root.gameObject.AddComponent<TouchStick>();
            stick.Knob = UIBox("Knob", root, new Vector2(.5f, .5f), Vector2.zero, new Vector2(56, 56), new Color(.94f, .7f, .15f, .85f));
            stick.Knob.GetComponent<Image>().raycastTarget = false;
            UIText(name, root, new Vector2(.5f, .5f), Vector2.zero, new Vector2(180, 35), 16);
            return stick;
        }
        private Button UIButton(string label, Vector2 anchor, Vector2 position, Action action)
        {
            var rect = UIBox(label, safeArea, anchor, position, new Vector2(150, 48), new Color(.1f, .16f, .21f, .9f));
            var button = rect.gameObject.AddComponent<Button>(); button.targetGraphic = rect.GetComponent<Image>(); button.onClick.AddListener(() => action());
            UIText(label, rect, new Vector2(.5f, .5f), Vector2.zero, rect.sizeDelta, 20);
            return button;
        }
        private Text UIText(string label, Transform parent, Vector2 anchor, Vector2 position, Vector2 size, int fontSize)
        {
            var go = new GameObject(label, typeof(RectTransform), typeof(Text)); var rect = go.GetComponent<RectTransform>(); rect.SetParent(parent, false);
            rect.anchorMin = rect.anchorMax = anchor; rect.anchoredPosition = position; rect.sizeDelta = size;
            var text = go.GetComponent<Text>(); text.font = font; text.fontSize = fontSize; text.color = Color.white; text.alignment = TextAnchor.MiddleCenter; text.raycastTarget = false; text.text = label;
            if (villageCharacter) { var shadow = go.AddComponent<Shadow>(); shadow.effectColor = new Color(0,0,0,.65f); shadow.effectDistance = new Vector2(1,-1); }
            return text;
        }
        private static RectTransform UIBox(string name, Transform parent, Vector2 anchor, Vector2 position, Vector2 size, Color color)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image)); var rect = go.GetComponent<RectTransform>(); rect.SetParent(parent, false);
            rect.anchorMin = rect.anchorMax = anchor; rect.anchoredPosition = position; rect.sizeDelta = size; go.GetComponent<Image>().color = color; return rect;
        }
        private void ApplySafeArea()
        {
            if (!safeArea) return;
            Rect area = Screen.safeArea; if (area == lastSafeArea && safeArea.anchorMax != Vector2.zero) return;
            lastSafeArea = area;
            safeArea.anchorMin = new Vector2(area.xMin / Mathf.Max(1, Screen.width), area.yMin / Mathf.Max(1, Screen.height));
            safeArea.anchorMax = new Vector2(area.xMax / Mathf.Max(1, Screen.width), area.yMax / Mathf.Max(1, Screen.height));
            safeArea.offsetMin = safeArea.offsetMax = Vector2.zero;
        }
        private Material MakeMaterial(Color color)
        { var m = materialTemplate ? new Material(materialTemplate) : new Material(Shader.Find("Universal Render Pipeline/Lit")); m.color = color; return m; }
        private static Transform Shape(string name, PrimitiveType type, Vector3 position, Vector3 scale, Material material)
        {
            var go = GameObject.CreatePrimitive(type); go.name = name; go.transform.position = position; go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = material; return go.transform;
        }
        private TextMesh WorldLabel(string label)
        {
            var text = new GameObject(label + " label").AddComponent<TextMesh>(); text.font = font; text.fontSize = 48; text.characterSize = villageCharacter ? .035f : .12f;
            text.anchor = TextAnchor.MiddleCenter; text.text = label; text.GetComponent<MeshRenderer>().sharedMaterial = font.material; return text;
        }
        private void OnApplicationPause(bool value)
        { suspended = value; movement?.ResetInput(); aiming?.ResetInput(); }
    }
}
