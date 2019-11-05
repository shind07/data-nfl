suppressMessages(library("nflscrapR"))
suppressMessages(library("optparse"))


main <- function() {
    # Argument parsing
    option_list <- list(
        make_option(c("-t", "--type"), type="character", default="reg", 
            help="week of games", metavar="character"),
        make_option(c("-y", "--year"), type="character", default=2019, 
            help="season year", metavar="character"),
        make_option(c("-w", "--week"), type="character", default=NULL, 
            help="week of games", metavar="character")
    ) 

    opt_parser <- OptionParser(option_list=option_list);
    args <- parse_args(opt_parser);

    if (is.null(args$year)) {
        stop("year argument not supplied.")
    }

    if (is.null(args$type)) {
        stop("game type argument not supplied.")
    }

    year <- args$year
    week <- args$week
    game_type <- args$type

    # Get games for week
    games <- scrape_game_ids(year, type=game_type)
    csv_name <- "/app/data/games_dump.csv"

    #write.table(games, sep=",", file=csv_name, col.names=!file.exists(csv_name), row.names=FALSE, append=file.exists(csv_name))
    write.table(games, sep=",", file=csv_name, col.names=TRUE, row.names=FALSE, append=FALSE)

}

if(!interactive()) {
    print("Running play_by_play script...")
    main()
    print("Ran play_by_play script.")
}