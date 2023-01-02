using AutoMapper;
using Microsoft.AspNetCore.Mvc;
using Scada.Dto;
using Scada.Models;

namespace Scada.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ReadingsController : ControllerBase
    {
        private readonly AppDbContext _context;
        private readonly IMapper _mapper;

        public ReadingsController(AppDbContext context, IMapper mapper)
        {
            _context = context;
            _mapper = mapper;
        }

        // GET: api/Readings
        [HttpGet]
        public ActionResult<IEnumerable<ReadingGetDto>> GetReadings(string rtuAddress, string deviceAddress, DateTime startDate, DateTime endDate)
        {
            var readings = from r in _context.Readings select r;

            if (!string.IsNullOrEmpty(rtuAddress))
            {
                readings = readings.Where(x => x.RtuAddress == rtuAddress);
            }

            if (!string.IsNullOrEmpty(deviceAddress))
            {
                readings = readings.Where(x => x.DeviceAddress == deviceAddress);
            }

            if (startDate != DateTime.MinValue)
            {
                readings = readings.Where(x => x.Date >= startDate);
            }

            if (endDate != DateTime.MinValue)
            {
                readings = readings.Where(x => x.Date <= endDate);
            }

            readings.Take(1000000);

            var readingDtos = new List<ReadingGetDto>();
            foreach (var reading in readings)
            {
                readingDtos.Add(_mapper.Map<ReadingGetDto>(reading));
            }
            return Ok(readingDtos);
        }

        // POST: api/Reading
        // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
        [HttpPost]
        public ActionResult<ReadingPostDto> PostReading(ReadingPostDto readingPostDto)
        {
            var reading = _mapper.Map<Reading>(readingPostDto);
            reading.Date = DateTime.UtcNow;
            _context.Readings.Add(reading);
            _context.SaveChanges();

            var devices = _context.Devices.Where(x => x.RtuAddress == readingPostDto.RtuAddress &&
                                                      x.DeviceAddress == readingPostDto.DeviceAddress);

            foreach (var device in devices)
            {
                device.PointData = readingPostDto.PointData;
            }
            _context.SaveChanges();

            return CreatedAtAction("GetReadings", new { id = reading.Id }, readingPostDto);
        }
    }
}
