<html>
    <?php
        // basic php that shows dynamic variables loaded into an html page
        date_default_timezone_set("America/Detroit");
        $name = "PHP Maestro";
        $browser = $_SERVER['HTTP_USER_AGENT'];
        echo "<h1>Hello, $name!</h1>";
        if (str_contains($_SERVER['HTTP_USER_AGENT'], 'Chrome')) {
            echo 'You are using Google Chrome!';
        } else {
            echo 'You are using ' . $browser . '.';
        };
        echo "<p>Today is " . date("l, F j, Y") . "</p>";
        echo "<p>The time is " . date("g:i A") . "</p>";
    ?>
</html>
