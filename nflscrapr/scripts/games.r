library("nflscrapR")
library("optparse")


main <- function() {
    # Argument parsing
    option_list <- list(
        make_option(c("-y", "--year"), type="character", default=NULL, 
                help="season year", metavar="character"),
        make_option(c("-w", "--week"), type="character", default=NULL, 
                help="week of games", metavar="character")
    ); 
    opt_parser <- OptionParser(option_list=option_list);
    args <- parse_args(opt_parser);

    if (is.null(args$year)) {
        stop("year argument not supplied.")
    }

    if (is.null(args$week)) {
        stop("week argument not supplied.")
    }

    year <- args$year
    week <- args$week

    if (typeof(week) != "integer") {
        week <- as.integer(week)
    }

    # Get games for week
    games <- scrape_game_ids(year, weeks=week)
    csv_name <- "/app/data/games.csv"
    write.table(games, sep=",", file=csv_name, col.names = !file.exists(csv_name), row.names=FALSE, append=TRUE)

}

if(!interactive()) {
    print("Running play_by_play script...")
    main()
    print("Ran play_by_play script.")
}