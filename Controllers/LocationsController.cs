namespace Scada.Controllers;

using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Scada;
using Scada.Models;
using AutoMapper;
using Scada.Dto;

[Route("api/[controller]")]
[ApiController]
public class LocationsController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IMapper _mapper;

    public LocationsController(AppDbContext context, IMapper mapper)
    {
        _context = context;
        _mapper = mapper;
    }

    // GET: api/Locations
    [HttpGet]
    public ActionResult<IEnumerable<LocationGetDto>> GetLocations()
    {
        var locations = new List<LocationGetDto>();
        foreach (var location in _context.Locations)
        {
            locations.Add(_mapper.Map<LocationGetDto>(location));
        }
        return Ok(locations);
    }

    // GET: api/Locations/5
    [HttpGet("{id}")]
    public ActionResult<LocationGetDto> GetLocation(int id)
    {
        var location = _context.Locations.Find(id);

        if (location == null)
        {
            return NotFound();
        }

        LocationGetDto locationGetDto = _mapper.Map<LocationGetDto>(location);

        return Ok(locationGetDto);
    }


    // POST: api/Locations
    // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
    [HttpPost]
    public ActionResult<LocationPostDto> PostLocation(LocationPostDto locationPostDto)
    {

        Location location = _mapper.Map<Location>(locationPostDto);

        _context.Locations.Add(location);
        _context.SaveChanges();

        return CreatedAtAction("GetLocation", new { id = location.Id }, locationPostDto);
    }

}

