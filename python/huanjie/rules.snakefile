# Here are some useful rules for one to grab

# transfer files to sudmantlab shared google drive
rule tfsudmant:
    input:
        result=config["distance_tables"],
        plot=config["distance_plots"]
    output:
        temp(touch(config["done"]))
    shell:
        """
        for var in {input}
        do
           rclone copy $var sudmantlab:projects/agingGeneRegulation/savio/$(date +'%Y%m%d')
        done
        """
