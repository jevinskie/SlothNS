<?php
function fib($n) {
    if ($n < 1) {
        return 0;
    } elseif ($n == 1) {
        return 1;
    } else {
        return fib($n-1) + fib($n-2);
    }
}

echo fib($_GET['n']);
?>

