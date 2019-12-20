suppressMessages(library("XML"))
suppressMessages(library("RCurl"))
suppressMessages(library("bitops"))
suppressMessages(library("nflscrapR"))
suppressMessages(library("optparse"))


main <- function() {
    # Argument parsing
    option_list <- list(
        make_option(c("-y", "--game"), type="character", 
            help="game id", metavar="character"),
        make_option(c("-f", "--file"), type="character", default=NULL, 
            help="file to write data to", metavar="character")
    ) 

    opt_parser <- OptionParser(option_list=option_list);
    args <- parse_args(opt_parser);

    if (is.null(args$game)) {
        stop("game id not given.")
    }

    if (is.null(args$file)) {
        stop("file name argument not supplied.")
    }

    game_id <- args$game
    csv_name <- args$file

    # Extract and dump data
    play_by_play <- scrape_json_play_by_play(game_id)
    write.table(play_by_play, sep=",", file=csv_name, col.names=TRUE, row.names=FALSE, append=FALSE)
}

if(!interactive()) {
    print("Running play_by_play script...")
    main()
    print("Ran play_by_play script.")
}