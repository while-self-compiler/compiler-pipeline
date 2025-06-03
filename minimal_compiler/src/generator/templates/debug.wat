
;; DEBUGGING

(import "env" "printf" (func $printf (param i32) (result i32)))


(;
  FOR DEBUGGING PURPOSES

  Definition:
  (import "env" "printf" (func $printf (param i32) (result i32)))

  Usage:
  (local.get $x)
  (call $printf)
  (drop)
;)