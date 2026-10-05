# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

I chose 4/5 because the correct information should be retrieved for most questions, while allowing for an occasional retrieval failure or edge case. A lower target like 3/5 would mean the system is failing to retrieve the answer too often to be considered reliable.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

I chose 5/5 because every answer should identify where its information came from, and there isn't a good reason to accept an answer that provides no source. This is an important requirement for being able to verify the system's responses.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

I chose 4/5 because the relevance gate should reliably recognize when the documents don't contain enough information, while allowing for an occasional mistake. A lower target like 3/5 would mean the system could confidently answer questions it cannot actually support too often.

---

## 4. Chunks preserve natural boundaries

In at least 4 of 5 randomly selected chunks, the chunk ends at a natural
sentence or section boundary and does not cut a sentence or thought between
chunks.


**Why this target:**

I chose 4/5 because a single imperfect chunk can happen from an edge case, but I still want the chunker to produce sensible boundaries consistently. The city_guides documents contain information that spans multiple sentences and is organized into labeled sections, so splitting in the middle of a sentence or section could leave important context incomplete.

---

## 5. Answers are grounded in retrieved documents

For at least 4 of my 5 questions, every factual claim in the system's answer
is directly supported by information in the retrieved source documents.



**Why this target:**

I chose 4/5 because the system should be reliably grounded in the provided
documents, while allowing for an occasional error or edge case. A lower target
like 3/5 would allow too many unsupported claims and would not give me enough
confidence that the system consistently answers based on the documents.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
