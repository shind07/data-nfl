suppressMessages(library("XML"))
suppressMessages(library("RCurl"))
suppressMessages(library("bitops"))
suppressMessages(library("nflscrapR"))
suppressMessages(library("optparse"))


main <- function() {
    # Argument parsing
    option_list <- list(
        make_option(c("-y", "--year"), type="character", default=2019, 
            help="season year", metavar="character"),
        make_option(c("-t", "--type"), type="character", default="reg", 
            help="week of games", metavar="character"),
        make_option(c("-f", "--file"), type="character", default=NULL, 
            help="file to write data to", metavar="character")
    ) 

    opt_parser <- OptionParser(option_list=option_list);
    args <- parse_args(opt_parser);

    if (is.null(args$year)) {
        stop("year argument not supplied.")
    }

    if (is.null(args$type)) {
        stop("game type argument not supplied.")
    }

    if (is.null(args$file)) {
        stop("game type argument not supplied.")
    }

    year <- args$year
    game_type <- args$type  
    csv_name <- args$file
    # Get games for week
    games <- scrape_game_ids(year, type=game_type)

    #write.table(games, sep=",", file=csv_name, col.names=!file.exists(csv_name), row.names=FALSE, append=file.exists(csv_name))
    write.table(games, sep=",", file=csv_name, col.names=TRUE, row.names=FALSE, append=FALSE)

}

if(!interactive()) {
    print("Running games script...")
    main()
    print("Ran games script.")
}