namespace Scada;

using System.Text;
using AutoMapper;
using Scada.Dto;
using Scada.Models;
using Newtonsoft.Json.Linq;

public class AutoMapping : Profile
{
    public AutoMapping()
    {
        //CreateMap<JObject, string>().ConstructUsing(jObject => jObject.ToString());
        //CreateMap<string, JObject>().ConstructUsing(s => JObject.Parse(s));
        CreateMap<Location, LocationGetDto>();
        CreateMap<LocationPostDto, Location>();
        CreateMap<Device, DeviceGetDto>();
        CreateMap<DevicePostDto, Device>();
        CreateMap<DisplayPoint, DisplayPointGetDto>();
        CreateMap<DisplayPointPostDto, DisplayPoint>();
        CreateMap<Reading, ReadingGetDto>();
        CreateMap<ReadingPostDto, Reading>();
    }
}