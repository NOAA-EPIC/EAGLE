There are a few files I am assuming you have here:

1) conservative_1059x1799_211x359.nc
2) conservative_719x1440_180x360.nc
3) inference-last.ckpt
4) global_one_degree.nc
5) hrrr_15km.nc

Just copy these over from your model recent nested_eagle run.

During operational inference we would just want static versions of these files always readily available to load.

To run inference in near real time:
1) Run submit_data.sh
2) Run submit_inference.sh

I have not done wxvx yet.

Also, this is by no means the best way to do it. But, it works as a starting point from a workflow standpoint. Basically, imagine some sort of workflow kicking this off with a regular cadence and it would get the job done. 